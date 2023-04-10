import socket
import hashlib
import json
from datetime import datetime

MESSAGE_SIZE = 4096

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
    
    
    # Start process
    while True:
        
        client_conn, client_addr = s.accept()
        
        # Receive request data from socket
        payload = client_conn.recv(MESSAGE_SIZE)
        payload_json = json.loads(payload.decode())
        print(f"Payload JSON is : {payload_json}")
        
        # Senc back ack to parent instance
        # use example date + json
        _sample_return_msg = {
            "datetime": datetime.now().strftime("%Y/%m/%d %H:%m:%S"),
            "json_result": payload_json
        }
        client_conn.send(str.encode(json.dumps(_sample_return_msg)))
        
        print("Message sent back to client")
        
        client_conn.close()


if __name__ == '__main__':
    main()