# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Utilities
import time
import sys
import json
import base64
import os
import socket
import subprocess
import traceback
import argparse
import logging
from cryptography.fernet import Fernet
import boto3

sys.path.insert(1, '.')
from kms import nitroKms

MESSAGE_SIZE = 4096

# Initialize kms object
nitro_kms = nitroKms()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
debug = False
NUM_BYTES_FOR_LEN = 4
TEMP_IMAGE_FILE_LOCATION = "/tmp/temp_file.png"


# def decrypt_cipher(access, secret, token, ciphertext, region):
def decrypt_cipher(credential, encrypted_data, region):
    """
    use KMS Tool Enclave Cli to decrypt cipher text, via nitro_kms
    """
    # Decrypt encrypted data_key by KMS Decrypt API with attestation
    # Key metadata included in Ciphertextblob, return bytes
    datakeyPlainTextBase64 = nitro_kms.call_kms_decrypt(credential, region, encrypted_data)
    print("decrypted datakey", datakeyPlainTextBase64)

    # datakeyPlainTextBase64 return format is similiar to "PLAINTEXT: Oxxxxxxxxxxxxx="
    # So need to split and pick 2nd part (position 1)
    plaintext_content = datakeyPlainTextBase64.split(":")[1].strip()
    return plaintext_content


def get_plaintext(payload):
    """
    prepare inputs and invoke decrypt function
    """

    # take all data from client
    encrypted_file = payload['data_in_base64']

    # Get irsa_credential from payload
    irsa_credential = payload['irsa_credential']

    # adhoc change for resolving issue - unable to os.getenv 
    region = payload['region']

    file_contents = base64.b64decode(encrypted_file.encode('utf-8'))

    # # The first NUM_BYTES_FOR_LEN tells us the length of the encrypted data key
    # # Bytes after that represent the encrypted file data
    # data_key_encrypted_len = int.from_bytes(file_contents[:NUM_BYTES_FOR_LEN], byteorder="big") + NUM_BYTES_FOR_LEN
    # data_key_encrypted = file_contents[NUM_BYTES_FOR_LEN:data_key_encrypted_len]

    # local_data_key_encrypted = base64.b64encode(data_key_encrypted)
    # local_data_key_encrypted_string = local_data_key_encrypted.decode('utf-8')

    # # Decrypt the data key before using it
    # data_key_plaintext = decrypt_cipher(irsa_credential, local_data_key_encrypted_string, region)

    # f = Fernet(data_key_plaintext)
    # file_contents_decrypted = f.decrypt(file_contents[data_key_encrypted_len:])

    return file_contents


def run_classifier(file_contents, classifier_view):
    """
      file_contents   : Decrypted image file
      classifier_view : L-CC, R-CC, L-MLO, R-MLO, Same as image type

      call the run_single.sh and pass file location and VIEW into that

      Return classifier result:
      (like) {"benign": 0.040191877633333206, "malignant": 0.008045288734138012}
    """

    image_64_encode = base64.urlsafe_b64encode(file_contents)
    image_decoded_data = base64.urlsafe_b64decode(image_64_encode)

    with open(TEMP_IMAGE_FILE_LOCATION, 'wb') as f:
        f.write(image_decoded_data)

    """
      Call process
    """
    os.chdir("/app/breast_cancer_classifier")
    proc = subprocess.Popen(
        [
            "bash",
            "run_single.sh",
            TEMP_IMAGE_FILE_LOCATION,
            classifier_view
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    ret = proc.communicate()
    if ret[0]:
        b64text = proc.communicate()[0].decode()
        plaintext = b64text
        return plaintext
    else:
        return f"Unable to run detection from image. Error msg: {proc.communicate()[1].decode()}"

    return


def receive_all(sock):
    buffer_size = 4096  # 4 KiB
    data = b''
    while True:
        part = sock.recv(buffer_size)
        data += part
        if len(part) < buffer_size:
            # either 0 or end of data
            break
    return data


def decrypt_model(payload):
    """Decrypt a file encrypted by encrypt_file()"""

    # Get irsa_credential from payload
    irsa_credential = payload['irsa_credential']

    # adhoc change for resolving issue - unable to os.getenv 
    region = payload['region']

    # Read the encrypted file into memory
    src_dir = "/app/breast_cancer_classifier/models/"
    file_name = "ImageOnly__ModeImage_weights.p"
    output_dir = "/app/breast_cancer_classifier/models/"
    with open("{}/{}.encrypted".format(src_dir, file_name), "rb") as file:
        file_contents = file.read()

    # The first NUM_BYTES_FOR_LEN tells us the length of the encrypted data key
    # Bytes after that represent the encrypted file data
    data_key_encrypted_len = int.from_bytes(file_contents[:NUM_BYTES_FOR_LEN], byteorder="big") + NUM_BYTES_FOR_LEN
    data_key_encrypted = file_contents[NUM_BYTES_FOR_LEN:data_key_encrypted_len]

    local_data_key_encrypted = base64.b64encode(data_key_encrypted)
    local_data_key_encrypted_string = local_data_key_encrypted.decode('utf-8')

    # Decrypt the data key before using it
    data_key_plaintext = decrypt_cipher(irsa_credential, local_data_key_encrypted_string, region)
    if data_key_plaintext is None:
        return False

    # Decrypt the rest of the file
    f = Fernet(data_key_plaintext)
    file_contents_decrypted = f.decrypt(file_contents[data_key_encrypted_len:])

    # Write the decrypted file contents
    with open(output_dir + file_name, 'wb') as file_decrypted:
        file_decrypted.write(file_contents_decrypted)


def encrypt_inference_result(data_key_plaintext, data_key_encrypted, inference_result):
    f = Fernet(data_key_plaintext)
    encrypted_inference_result = f.encrypt(inference_result)

    with open(ENCRYPTED_INFERENCE_RESULT_LOCATION, 'wb') as file_encrypted:
        file_encrypted.write(len(data_key_encrypted).to_bytes(NUM_BYTES_FOR_LEN, byteorder='big'))
        file_encrypted.write(data_key_encrypted)
        file_encrypted.write(encrypted_inference_result)

    with open(ENCRYPTED_INFERENCE_RESULT_LOCATION, 'rb') as r:
        final_encrypted_inference_ciphertext = r.read()

    return final_encrypted_inference_ciphertext


def main():
    print("Server is initializing...")

    inference_results: dict
    is_model_decrypted = False

    ################################################################################

    # Default to Production settings
    socket_address = socket.AF_VSOCK
    cid = socket.VMADDR_CID_ANY  # Listen to any CID

    # Create VSock socket object
    s = socket.socket(socket_address, socket.SOCK_STREAM)

    # Listened port should match to client running on parent EC2 instance (Pod)
    port = 5000

    # Bind the socket to (CID, PODT)
    s.bind((cid, port))

    # Start to listen
    s.listen()

    logging.info(f"Started server on port {port} and cid {cid} and pid {os.getpid()}")

    while True:
        print('Waiting to accept...')
        c, address = s.accept()
        payload = receive_all(c)

        response = {}

        if not is_model_decrypted:
            print('Model Pending to be decrypted...')

        try:

            payload_decoded = json.loads(payload.decode())

            file_content = get_plaintext(payload_decoded)
            # decrypted_data_key = None

            # if decrypt_response == "KMS Error. Decryption Failed.":
            #     response["error"] = decrypt_response
            # else:
            #     decrypted_data_key = decrypt_response

            if not is_model_decrypted:
                decrypt_model(payload_decoded)
                is_model_decrypted = True
                logging.info("Model file decrypted, now ready to serve incoming request...")

            inference_results = run_classifier(file_content,
                                               classifier_view=payload_decoded['classifier_view'])

            print(f"Inference result is :{inference_results}.")

            response["classification"] = json.loads(inference_results)
            json_response = json.dumps(response, default=vars)
            logging.info(json_response)

            # encrypted_inference_result = encrypt_inference_result(decrypted_data_key, data_key_encrypted,
            #                                                       json_response.encode())

            c.send(json_response.encode())

            c.close()

        except Exception as e:
            c.close()
            logging.error(f'Exception raised: {e}')
            traceback.print_exc()


if __name__ == '__main__':
    main()
