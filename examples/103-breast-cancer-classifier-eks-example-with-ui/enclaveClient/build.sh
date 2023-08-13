#!/bin/bash

DOCKER_IMAGE_NAME="breast-cancer-classifier-client-backend"

# Create repository if not exist
aws ecr create-repository --repository-name ${DOCKER_IMAGE_NAME} --region ${REGION}

# Build image
docker build -t ${DOCKER_IMAGE_NAME} .

ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)

aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
docker tag ${DOCKER_IMAGE_NAME}:latest ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${DOCKER_IMAGE_NAME}:latest
docker push $ACCOUNT_ID.dkr.ecr.${REGION}.amazonaws.com/${DOCKER_IMAGE_NAME}:latest

kubectl delete -f deploy.yaml
kubectl apply -f deploy.yaml
