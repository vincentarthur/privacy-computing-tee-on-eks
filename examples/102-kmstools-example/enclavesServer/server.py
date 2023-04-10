import socket
import hashlib
import json
import os
import base64
from datetime import datetime
import boto3
import sys

sys.path.insert(1, '.')

from kms import nitroKms

MESSAGE_SIZE = 4096

# Initialize kms object
nitro_kms = nitroKms()

def process_data(credential, encrypted_data, region, kms_key_id):

    # Decrypt encrypted data_key by KMS Decrypt API with attestation
    # Key metadata included in Ciphertextblob, return bytes 
    datakeyPlainTextBase64 = nitro_kms.call_kms_decrypt(credential, region, encrypted_data)
    print("decrypted datakey",datakeyPlainTextBase64)
    plaintext_content = datakeyPlainTextBase64.split(":")[1].strip()
    
    base64_bytes = plaintext_content.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('ascii')

    return {
        "decoded_message": message
    }


def main():
    print("Server is initializing...")
    
    # FOR DEBUG
    # socket_address = socket.AF_INET
    # cid = '127.0.0.1'
    
    # For ACTUAL
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
    
    # Get AWS_REGION from environment
    # unable to get ???
    # region = os.getenv("REGION")
    
    # Start process
    while True:
        
        client_conn, client_addr = s.accept()
        
        # Receive request data from socket
        payload = client_conn.recv(MESSAGE_SIZE)
        payload_json = json.loads(payload.decode())
        print(f"Payload JSON is : {payload_json}")
        
        # Example: We expect the JSON payload includes:
        # 1) S3_URI of files to be processed
        # 2) KMS key for decryption
        # 3) IRSA credential
        
        # Get KMS Key ID
        kms_key_id = payload_json['kms_key_id'] # arn_id
        
        # Get encrypted_data
        encrypted_data = payload_json['encrypted_data']
        
        # Get irsa_credential from payload
        irsa_credential = payload_json['irsa_credential']
        
        # adhoc change for resolving issue - unable to os.getenv 
        region = payload_json['region']
        
        resp = process_data(irsa_credential, encrypted_data, region, kms_key_id)
        
        client_conn.send(str.encode(json.dumps(resp)))
        
        print("Message sent back to client")
        
        client_conn.close()


if __name__ == '__main__':
    main()