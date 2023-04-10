FROM enclave_base

# Install python for running the server and net-tools for modifying network config
RUN yum install python3 iproute   -y

WORKDIR /home

# COPY requirements.txt ./
COPY server.py ./
COPY libnsm.so /usr/lib64/
# COPY kms.py ./
# COPY kmstool_enclave_cli ./

# RUN pip3 install -r requirements.txt

# RUN chmod +x kmstool_enclave_cli

CMD ["python3", "/home/server.py"]
