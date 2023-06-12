FROM enclave_base

# Install python for running the server and net-tools for modifying network config
RUN yum install python3 iproute jq -y

WORKDIR /app

COPY images/ ./
COPY envelope-encryption/ ./
COPY requirements.txt ./
COPY client.py ./
COPY libnsm.so /usr/lib64/

RUN pip3 install -r requirements.txt --no-cache

CMD ["python3", "/app/client.py"]
