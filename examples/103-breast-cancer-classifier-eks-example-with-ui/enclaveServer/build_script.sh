#!/bin/bash

DOCKER_IMAGE_NAME="breast-cancer-classifier"

# Create repository if not exist
aws ecr describe-repositories --repository-names ${DOCKER_IMAGE_NAME} --region ${REGION} || aws ecr create-repository --repository-name ${DOCKER_IMAGE_NAME} --region ${REGION}

# Build images
docker build -t ${DOCKER_IMAGE_NAME}:latest .
nitro-cli build-enclave --docker-uri ${DOCKER_IMAGE_NAME}:latest --output-file ${DOCKER_IMAGE_NAME}.eif
docker build -t ${DOCKER_IMAGE_NAME}:latest_eif -f Dockerfile.eif .

ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)

aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
docker tag ${DOCKER_IMAGE_NAME}:latest_eif ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${DOCKER_IMAGE_NAME}:latest_eif
docker push $ACCOUNT_ID.dkr.ecr.${REGION}.amazonaws.com/${DOCKER_IMAGE_NAME}:latest_eif

kubectl delete -f deploy.yaml
kubectl apply -f deploy.yaml
