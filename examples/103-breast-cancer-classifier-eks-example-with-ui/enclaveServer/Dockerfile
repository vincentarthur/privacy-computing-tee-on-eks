# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# // SPDX-License-Identifier: MIT-0

#this is the enclave image
FROM enclave_base

# Install python for running the server and net-tools for modifying network config
RUN yum install python3 iproute -y
ENV AWS_STS_REGIONAL_ENDPOINTS=regional
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/app
#ENV AWS_DEFAULT_REGION=us-east-1

WORKDIR /app


COPY libnsm.so /usr/lib64/
COPY kms.py ./
COPY kmstool_enclave_cli ./
COPY requirements.txt ./
COPY server.py ./
COPY breast_cancer_classifier/ /app/breast_cancer_classifier/

RUN pip3 install -r /app/requirements.txt --no-cache


RUN chmod +x kmstool_enclave_cli

CMD ["python3", "/app/server.py"]