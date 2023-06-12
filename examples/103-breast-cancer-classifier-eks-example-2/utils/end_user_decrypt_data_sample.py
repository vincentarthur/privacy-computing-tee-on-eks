import boto3
import base64
from cryptography.fernet import Fernet

NUM_BYTES_FOR_LEN = 4
LOCAL_FILE_LOCATION = './temp.result'

"""
    This example runs on end user sider (data owner), who raises the inference request with encrypted data.
    The inference data is being encrypted with same KMS key from data owner, so only same KMS key can decrypt
    the data.
    
    Assuming that you already have the encrypted data saved into S3. 
    What this script does is to 
    1. read the file content 
    2. read encrypted data key and raise request to get decrypt key
    3. decrypt result to plaintext 
"""


def decrypt_data_key(data_key_encrypted):
    """Decrypt an encrypted data key

    :param data_key_encrypted: Encrypted ciphertext data key.
    :return Plaintext base64-encoded binary data key as binary string
    :return None if error
    """

    # Decrypt the data key
    kms_client = boto3.client('kms')
    try:
        response = kms_client.decrypt(CiphertextBlob=data_key_encrypted)
    except Exception as e:
        print(e)
        return None

    # Return plaintext base64-encoded binary data key
    return base64.b64encode((response['Plaintext']))


def decrypt_result(result_in_bytes):
    data_key_encrypted_len = int.from_bytes(result_in_bytes[:NUM_BYTES_FOR_LEN],
                                            byteorder='big') \
                             + NUM_BYTES_FOR_LEN
    data_key_encrypted = result_in_bytes[NUM_BYTES_FOR_LEN:data_key_encrypted_len]

    # Decrypt the data key before using it
    data_key_plaintext = decrypt_data_key(data_key_encrypted)
    if data_key_plaintext is None:
        return False

    # Decrypt the rest of the file
    f = Fernet(data_key_plaintext)
    plaintext_result = f.decrypt(result_in_bytes[data_key_encrypted_len:])

    # print response
    print(plaintext_result)

    return plaintext_result


def download_encrypted_data_file(bucket_name, object_name):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, object_name, LOCAL_FILE_LOCATION)


if __name__ == "__main__":
    # 1. Download and read result
    download_encrypted_data_file('<Input_bucketname>', '<input_object_name_with_prefix>')
    with open(LOCAL_FILE_LOCATION, 'rb') as file:
        file_contents = file.read()

    # 2. Decrypt
    decrypt_result(file_contents)
