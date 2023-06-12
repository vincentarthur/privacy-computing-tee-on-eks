#!/bin/bash

# This is only example of vwmc@amazon.com

docker build -t breast-cancer-classifier:latest .
nitro-cli build-enclave --docker-uri breast-cancer-classifier:latest --output-file breast-cancer-classifier.eif
docker build -t breast-cancer-classifier:latest_eif -f Dockerfile.eif .

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 536704830979.dkr.ecr.us-east-1.amazonaws.com

docker tag breast-cancer-classifier:latest_eif 536704830979.dkr.ecr.us-east-1.amazonaws.com/breast-cancer-classifier:latest_eif

docker push 536704830979.dkr.ecr.us-east-1.amazonaws.com/breast-cancer-classifier:latest_eif