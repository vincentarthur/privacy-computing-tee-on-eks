# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Utilities
import time
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

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
debug = False
KMS_PROXY_PORT = "8001"
NUM_BYTES_FOR_LEN = 4
TEMP_IMAGE_FILE_LOCATION = "/tmp/temp_file.png"


def decrypt_cipher(access, secret, token, ciphertext, region):
    """
    use KMS Tool Enclave Cli to decrypt cipher text
    """

    proc = subprocess.Popen(
        [
            "/app/kmstool_enclave_cli",
            "--region", region,
            "--proxy-port", KMS_PROXY_PORT,
            "--aws-access-key-id", access,
            "--aws-secret-access-key", secret,
            "--aws-session-token", token,
            "--ciphertext", ciphertext,
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
        return f"KMS Error.Decryption Failed. Error msg: {proc.communicate()[1].decode()}"


def get_plaintext(payload):
    """
    prepare inputs and invoke decrypt function
    """

    # take all data from client
    access = payload['access_key_id']
    secret = payload['secret_access_key']
    token = payload['token']
    encrypted_file = payload['encrypted_file']
    region = payload['region']

    file_contents = base64.b64decode(encrypted_file.encode('utf-8'))
    # file_contents = base64.b64decode(encrypted_file.encode())
    # The first NUM_BYTES_FOR_LEN tells us the length of the encrypted data key
    # Bytes after that represent the encrypted file data
    data_key_encrypted_len = int.from_bytes(file_contents[:NUM_BYTES_FOR_LEN], byteorder="big") + NUM_BYTES_FOR_LEN
    data_key_encrypted = file_contents[NUM_BYTES_FOR_LEN:data_key_encrypted_len]

    local_data_key_encrypted = base64.b64encode(data_key_encrypted)
    local_data_key_encrypted_string = local_data_key_encrypted.decode('utf-8')  # 'utf-8'

    # Decrypt the data key before using it
    data_key_plaintext = decrypt_cipher(access, secret, token, local_data_key_encrypted_string, region)

    f = Fernet(data_key_plaintext)
    file_contents_decrypted = f.decrypt(file_contents[data_key_encrypted_len:])

    return data_key_plaintext, file_contents_decrypted


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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Whether to run in debug mode")

    return parser.parse_args()


def decrypt_model(payload):
    """Decrypt a file encrypted by encrypt_file()"""

    # take all data from client
    access = payload['access_key_id']
    secret = payload['secret_access_key']
    token = payload['token']
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
    data_key_plaintext = decrypt_cipher(access, secret, token, local_data_key_encrypted_string, region)
    if data_key_plaintext is None:
        return False

    # Decrypt the rest of the file
    f = Fernet(data_key_plaintext)
    file_contents_decrypted = f.decrypt(file_contents[data_key_encrypted_len:])

    # Write the decrypted file contents
    with open(output_dir + file_name, 'wb') as file_decrypted:
        file_decrypted.write(file_contents_decrypted)


def main():
    args = parse_args()
    global debug
    debug = args.debug
    inference_results: dict
    IS_MODEL_DECRYPTED = True

    ################################################################################

    # Default to Production settings
    socket_address = socket.AF_VSOCK
    port = 5000
    cid = socket.VMADDR_CID_ANY
    if debug:
        # For Debugging
        logging.basicConfig(level=logging.DEBUG)
        socket_address = socket.AF_INET
        cid = '127.0.0.1'

    s = socket.socket(socket_address, socket.SOCK_STREAM)
    s.bind((cid, port))
    s.listen()
    logging.info(f"Started server on port {port} and cid {cid} and pid {os.getpid()}")

    detector = None

    while True:
        print('Waiting to accept...')
        c, address = s.accept()
        payload = receive_all(c)

        min_score_pct = 50
        objects_detected = []
        response = {}

        if not IS_MODEL_DECRYPTED:
            print('Model Pending to be decrypted...')

        try:

            payload_decoded = json.loads(payload.decode())

            decrypt_response, file_contents_decrypted = get_plaintext(payload_decoded)

            if decrypt_response == "KMS Error. Decryption Failed.":
                response["error"] = decrypt_response

            if not IS_MODEL_DECRYPTED:
                decrypt_model(payload_decoded)
                IS_MODEL_DECRYPTED = True
                logging.info("Model file decrypted, now ready to serve incoming request...")

            inference_results = run_classifier(file_contents_decrypted,
                                               classifier_view=payload_decoded['classifier_view'])

            print(f"Inference result is :{inference_results}.")

            response["classification"] = json.loads(inference_results)
            json_response = json.dumps(response, default=vars)
            logging.info(json_response)

            c.send(str.encode(json_response))
            c.close()
        except Exception as e:
            c.close()
            logging.error(f'Exception raised: {e}')
            traceback.print_exc()


if __name__ == '__main__':
    main()
