# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import json
import base64
import socket
import subprocess
import argparse
import requests
import boto3
import os


RECEIVE_MSG_QUOTA = 65535


def retrieve_irsa_tokens():
    # cred.access_key, cred.secret_key, cred.token(session_token)
    try:
        irsa_cred = boto3.session.Session().get_credentials()
        return {
            "aws_access_key_id": irsa_cred.access_key,
            "aws_secret_access_key": irsa_cred.secret_key,
            "aws_session_token": irsa_cred.token
        }

    except Exception as e:
        print("Error occurred : {}".format(str(e)))
        return None


def read_file(path):
    with open(path, "rb") as file:
        file_contents = file.read()
    return file_contents


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filePath", required=True, help="Path of the image file")

    return parser.parse_args()


def main():

    args = parse_args()
    image_path = args.filePath

    _region = os.getenv('REGION')
    cid = int(os.getenv('CID')) # Listen to any CID

    # Read file from File Path
    encrypted_file  = read_file(image_path)
    image_name      = image_path[image_path.rfind("/"):]
    classifier_view = image_name[:image_name.index(".")][image_name.index("_")+1:].replace('_', '-')

    # Convert file to base64 prior to sending to server.py
    encrypted_file_base64 = base64.b64encode(encrypted_file)
    encrypted_file_base64_string = encrypted_file_base64.decode('utf-8')

    # Construct JSON doc
    # server_json_payload = prepare_server_request(encrypted_file_base64_string, classifier_view)

    # Hardcode workload
    WORKLOAD = {
        "irsa_credential": retrieve_irsa_tokens(),
        "region"         : _region,
        'encrypted_data' : encrypted_file_base64_string,
        'classifier_view': classifier_view
    }

    # Send data to server
    # The port should match the server running in enclave
    port = 5000
    # Create a vsock socket object and Connect to the server
    s = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)

    s.connect((cid, port))

    # receive data from the server
    s.send(str.encode(json.dumps(WORKLOAD)))

    # Retrieve resposne
    response = s.recv(RECEIVE_MSG_QUOTA).decode()
    print(f"Received msg from Server: {response}")

    # close the connection
    s.close()
    exit()


if __name__ == '__main__':
    main()
