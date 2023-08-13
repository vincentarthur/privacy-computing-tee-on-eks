from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin
import json
import base64
import socket
import subprocess
import argparse
import requests
import boto3
import os
import uuid
import logging
from botocore.exceptions import ClientError
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for whole app

TMP_LOCAL_STORAGE = "/tmp"
port = 5000
WEB_APP_PORT = 5050
RECEIVE_MSG_QUOTA = 65535
IMAGE_SUFFIX_LIST = ['png', 'jpg', 'jpeg']

s3_res = boto3.resource('s3')
s3_cli = boto3.client('s3')
_region = os.getenv('REGION')
cid = int(os.getenv('CID'))  # Listen to any CID


def download_s3_file(bucket_name, file_name, local_file):
    """
    Function for downloading S3 file into local storage
    """
    s3_cli.download_file(
        Bucket=bucket_name,
        Key=file_name,
        Filename=local_file
    )


def read_image_into_base64(path):
    """
    Read and convert RAW image into Base64 format.
    """
    with open(path, "rb") as file:
        file_contents = file.read()
    return base64.b64encode(file_contents).decode("utf-8")


def retrieve_irsa_tokens():
    """
    Retrieve IRSA token from EKS Node group
    """
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


def send_request_to_enclaves(workload):
    """
    Connect to VSOCK - should this be changed to long-connection??
    """
    s = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
    s.connect((cid, port))

    # receive data from the server
    s.send(str.encode(json.dumps(workload)))

    # Retrieve resposne
    response = s.recv(RECEIVE_MSG_QUOTA).decode()
    s.close()

    return response


@app.route('/', methods=['GET'])
@cross_origin()
def index():
    """
    Verify if traffic works.
    """
    return "Traffic works"


@app.route('/api/list_images', methods=['GET'])
@cross_origin()
def list_all_images():
    """
    List all images according to S3 Bucket & folder.
    Expect parameter:
    - images_s3_location
    """

    print("Request received.")

    images_s3_bucket_location = os.getenv('IMAGES_S3_BUCKET_LOCATION')
    s3_bucket_name, folder_prefix = images_s3_bucket_location.split("/")

    objs_raw = s3_cli.list_objects_v2(
        Bucket=s3_bucket_name,
        Prefix=folder_prefix,
    )['Contents']

    objs = json.loads(json.dumps(objs_raw, default=str))

    images_list = [
        {
            "image_name": obj['Key'].split("/")[-1],
            "image_location": f"s3://{s3_bucket_name}/{obj['Key']}",
            # Generate Presigned URL for UI to retrieve
            "presigned_url": s3_cli.generate_presigned_url(
                'get_object', Params={
                    'Bucket': s3_bucket_name,
                    'Key': "{}/{}".format("thumbnails", obj['Key'].split("/")[-1])},
                ExpiresIn=300),  # 1hour
            "last_modified": str(obj['LastModified'])  # datetime.strftime(obj['LastModified'], '%Y/%m/%d %H:%M:%S')
        }
        for obj in objs if obj['Key'].split(".")[-1].lower() in IMAGE_SUFFIX_LIST
    ]

    return {
        "images": images_list
    }


@app.route('/api/predict', methods=['POST', 'OPTIONS'])
@cross_origin()
def predict():
    """
       Request should contain:
       - image_s3_path
    """

    data = request.get_json()
    try:
        image_s3_path = data['image_s3_path']
    except KeyError:
        response = """{
            "message": "Missing image location."
        }
        """
        return response

    image_s3_path_no_scheme = image_s3_path[5:]
    bucket_name = image_s3_path_no_scheme[:image_s3_path_no_scheme.find("/")]
    prefix = image_s3_path_no_scheme[image_s3_path_no_scheme.find("/") + 1:image_s3_path_no_scheme.rfind('/')]
    image_name = image_s3_path_no_scheme[image_s3_path_no_scheme.rfind('/') + 1:]

    local_file_path = f"{TMP_LOCAL_STORAGE}/{image_name}"

    # like L-CC / L-MO 
    classifier_view = image_name[:image_name.index(".")][image_name.index("_") + 1:].replace('_', '-')

    """
    Steps:
    1. Download S3 file to local storage
    2. Pass image (no encryption) to Enclave for prediction
    3. Get and Return result back to UI for display
    4.(X) (Optional) Write to DynamoDB
    """

    # 1. Download S3 file into local storage
    try:
        download_s3_file(
            bucket_name=bucket_name,
            file_name=f"{prefix}/{image_name}",
            local_file=local_file_path
        )
    except Exception as e:
        print(f"Unable to download file: {image_s3_path}", e)

        response = """{
            "message": "Unable to download file: {}. Error: {}"
        }""".format(image_s3_path, e)

        return response

    # 2. Pass image to Enclaves
    data_in_base64_string = read_image_into_base64(local_file_path)
    WORKLOAD = {
        "irsa_credential": retrieve_irsa_tokens(),
        "region": _region,
        'data_in_base64': data_in_base64_string,
        'classifier_view': classifier_view
    }

    response = send_request_to_enclaves(workload=WORKLOAD)

    # 3. Get and Return result back to UI for display
    return json.dumps(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=WEB_APP_PORT)
