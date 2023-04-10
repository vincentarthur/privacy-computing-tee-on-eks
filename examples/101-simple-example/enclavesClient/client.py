import socket
import json
# import requests
import os

SAMPLE_REQUEST_MSG = '{"msg":"hello"}'
RECEIVE_MSG_QUOTA = 65535

def main():
    
    # FOR DEBUG
    # socket_address = socket.AF_INET
    # _cid = "127.0.0.1" #int(os.getenv('CID'))
    
    # FOR ACTUAL
    socket_address = socket.AF_VSOCK
    _cid = int(os.getenv('CID')) # Listen to any CID
    
    _port = 5000
    
    # Create VSOCK object
    s = socket.socket(socket_address, socket.SOCK_STREAM)
    
    # Connect to Server (pod?)
    s.connect((_cid, _port))
    
    # Send request to Server
    s.send(str.encode(json.dumps(SAMPLE_REQUEST_MSG)))
    
    
    # Retrieve resposne
    response = s.recv(RECEIVE_MSG_QUOTA).decode()
    print(f"Received msg from Server: {response}")
    
    s.close()



if __name__ == "__main__":
    main()