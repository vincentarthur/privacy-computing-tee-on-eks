import socket
import json
import os
import boto3

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

    
def retrieve_s3_encrypted_data(data_s3_uri):
    """
    Download the encrypted sample data for passing into Nitro Enclaves
    """
    
    _bucket_name_and_prefix = data_s3_uri[5:]
    _bucket_name            = _bucket_name_and_prefix[:_bucket_name_and_prefix.index('/')]
    _object_prefix          = _bucket_name_and_prefix[_bucket_name_and_prefix.index('/')+1:]
    
    s3_client = boto3.client('s3')
    
    # Get the file inside the S3 Bucket
    s3_response = s3_client.get_object(
        Bucket  = _bucket_name,
        Key     = _object_prefix
    )

    # Get the Body object in the S3 get_object() response
    s3_object_body = s3_response.get('Body')

    # Read the data in bytes format and convert it to string
    encrypted_data_content = s3_object_body.read().decode().strip('\n')
    
    return encrypted_data_content


def main():
    
    # FOR DEBUG
    # socket_address = socket.AF_INET
    # _cid = "127.0.0.1" #int(os.getenv('CID'))
    
    # FOR ACTUAL
    socket_address = socket.AF_VSOCK
    _cid = int(os.getenv('CID')) # Listen to any CID
    
    _port = 5000
    
    _kms_key_id            = os.getenv('KMS_KEY_ID')
    _encrypted_data_s3_uri = os.getenv('ENCRYPTED_DATA_S3_URI')
    _region                = os.getenv('REGION') 
    
    # Create VSOCK object
    s = socket.socket(socket_address, socket.SOCK_STREAM)
    
    # Connect to Server (pod?)
    s.connect((_cid, _port))
    
    # Hardcode workload
    WORKLOAD = {
        "kms_key_id":      _kms_key_id ,
        "encrypted_data":  retrieve_s3_encrypted_data(_encrypted_data_s3_uri),
        "irsa_credential": retrieve_irsa_tokens(),
        "region":          _region
    }
    
    # Send request to Server
    s.send(str.encode(json.dumps(WORKLOAD)))
    
    # Retrieve resposne
    response = s.recv(RECEIVE_MSG_QUOTA).decode()
    print(f"Received msg from Server: {response}")
    
    s.close()



if __name__ == "__main__":
    main()