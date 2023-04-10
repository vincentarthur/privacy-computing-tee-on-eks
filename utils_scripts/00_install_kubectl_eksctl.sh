#!/bin/bash

set -e

KUBECTL_VERSION=$1

PLATFORM=amd64
KUBECTL_VERSION=${KUBECTL_VERSION:=1.22}


# Install kubectl if not exist
echo "Install kubectl..."
curl -o kubectl https://s3.us-west-2.amazonaws.com/amazon-eks/${KUBECTL_VERSION}/2022-10-31/bin/linux/${PLATFORM}/kubectl
openssl sha1 -sha256 kubectl # check sha256
chmod +x ./kubectl
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc

kubectl version --short --client
echo "Installed kubectl."


echo "Install eksctl..."
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
eksctl version
echo "Installed eksctl."
