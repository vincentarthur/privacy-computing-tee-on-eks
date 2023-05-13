# // Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# // SPDX-License-Identifier: MIT-0

#this is the enclave image
FROM enclave_base

# Install python for running the server and net-tools for modifying network config
RUN yum install python3 iproute -y
ENV AWS_STS_REGIONAL_ENDPOINTS=regional
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/app
ENV AWS_DEFAULT_REGION=us-east-2

WORKDIR /app

COPY breast_cancer_classifier/ /app/breast_cancer_classifier/
COPY requirements.txt ./
RUN pip3 install -r /app/requirements.txt --no-cache

COPY server.py ./
COPY run.sh ./

RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]