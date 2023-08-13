FROM enclave_base

# Install python for running the server and net-tools for modifying network config
RUN yum install python3 iproute jq -y
EXPOSE 5050

WORKDIR /app

COPY requirements.txt ./
COPY app.py ./

RUN pip3 install -r requirements.txt --no-cache

CMD ["python3", "/app/app.py"]
