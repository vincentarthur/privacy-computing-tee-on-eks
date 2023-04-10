# Section A :  Prerequisites​

We need kubectl,helm and AWS CLI to complete the setup of DataHub in AWS environment. We can execute all the instructions either from local desktop or using AWS Cloud9. If you are using AWS Cloud9 please follow below instruction to spin up AWS Cloud9 or 
else skip to installation of kubectl,helm and AWS CLI section.
```
  # Please check what version of K8S now EKS supports and pass version numer to script below
  # https://docs.aws.amazon.com/eks/latest/userguide/platform-versions.html
  
  # Focus "Amazon EKS end of support" on this section: "Amazon EKS Kubernetes release calendar"
  
  # Run below command to install both kubectl & eksctl
  bash utils_scripts/00_install_kubectl_eksctl.sh <k8s version>
  
  example: bash utils_scripts/00_install_kubectl_eksctl.sh 1.24
```


## If you are using Cloud9

**Note** Create a Cloud9 instance with instance type of t3.small and increase the default size from 10GB to 50GB. Follow the instructions on the Cloud9 documentation to resize your EBS volume to at least 50GB.

https://docs.aws.amazon.com/cloud9/latest/user-guide/move-environment.html#move-environment-resize

## This guide requires the installation of following cli tools, with following version:


* __kubectl__ -  to manage kubernetes resources

  **version** - [Client Version: version.Info{Major:"1", Minor:"21", GitVersion:"v1.21.6"}]

  For downloading a specific version
  ```
  sudo curl --silent --location -o /usr/local/bin/kubectl \
   https://s3.us-west-2.amazonaws.com/amazon-eks/1.21.5/2022-01-21/bin/linux/amd64/kubectl

  sudo chmod +x /usr/local/bin/kubectl

  **Note**
    
    For installing Kubectl in Cloud9 , Please follow the below instructions

  Cloud9 normally manages IAM credentials dynamically. This isn’t currently compatible with the EKS IAM authentication, so we will disable it and rely on the IAM role instead.

  https://www.eksworkshop.com/020_prerequisites/k8stools/
  https://www.eksworkshop.com/020_prerequisites/iamrole/
  https://www.eksworkshop.com/020_prerequisites/ec2instance/
  https://www.eksworkshop.com/020_prerequisites/workspaceiam/

* __AWS CLI__ -	Install AWS CLI (version 2.X.x) or migrate AWS CLI version 1 to version 2 - 
https://docs.aws.amazon.com/cli/latest/userguide/cliv2-migration.html



```
aws --version
```
 this should point to aws cli version 2, if this is still pointing to older version close the terminal and start with a new terminal 



To use the above tools, you need to set up AWS credentials by following this [guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html).


# Section B : install cdk 2 /upgrade cdk 1 to cdk 2

## Installing and updating CDK

```
npm install -g aws-cdk@latest
```

*** In the case of error try to force it ***
```
npm install -g aws-cdk@latest --force
```

# Deployment Steps

clone the repo  - 
```
git clone https://git-codecommit.us-east-1.amazonaws.com/v1/repos/deploy-nitro-enclave-with-eks
```
### Important : Change cdk.json config values (ACCOUNT_ID, REGION) , cdk.json is present in the root directory of the code repo
And change the value of ACCOUNT_ID and REGION in cdk.json

```
python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
python3 -m pip install -r requirements.txt
```

This is needed one time per account. If you have never executed this before, then run this

```
cdk bootstrap aws://<account-id>/<aws-region>

```

# Configuration in cdk.json
## Mandatory Items needs to be changed:
  - ACCOUNT_ID
  - REGION
  - eks_version (because k8s version will be EOL(end-of-life) in time range, please check version now supports)
  - eks_node_ami_version (same as above)
  - enclaves_node_iam_role (what IAM role will be used in NE nodes, please create in advance)
  - enclaves_iam_role (what IAM roles will be used in, please create in advance)
  
## Optional Items to be changed:
  - create_new_vpc (True or False)
  - VPC CIDR
  - eks_node_instance_type
  - eks_node_disk_size
  - eks_node_quantity
  - eks_node_min_quantity / eks_node_max_quantity
  - _*enclaves_namespace*_ (A namespace will be created for dedicate workload, and will apply IRSA(IamRole for Service Account) to this ns)
  - _*enclaves_k8s_service_account*_ (K8s Service Account for ns above)

## Step 1 - Provision EKS and NitroEnclaves NodeGroups
##### Components includes: EKS / NitroEnclaves nodegroup / Arbiter Server
```
  bash 01_install.sh
```
Wait until the process completes, you will have below resources provisioned
```
  - 1 VPC (if "create_new_vpc" set to true in cdk.json)
  - 1 EKS cluster
  - 1 default EKS nodegroup
  - 1 NitroEnclaves EKS nodegroup
  - 1 Arbiter Server (for federated learning param exchange)
```

## Step 2 - Enable IRSA(Iam Role for Service Account)
This step is to provide advanced permission segregation when running container in K8S,
without using Instance Role but a dedicated IAM role.
```
  # Follow this guide to setup workload identity in EKS
  # https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html
  
  #bash 02_setup_irsa.sh <EKS cluster name>
  bash 02_setup_irsa.sh cluster-eks_enclaves
```
Wait until all steps complete then an EKS with NE is provisioned.

## How to verify if EKS works fine ?
When CDK provisioned, a command to update kubeconfig will be displayed on screen. Copy and execute (for example in Cloud9).
After executing that, the kubeconfig (~/.kube/config) will be updated with token
```
    # Similar to
    aws eks update-kubeconfig --name cluster-eks_enclaves --region xxxx --role-arn arn:aws:iam::<account_name>:role/EKS-Enclaves-ClusterAdminRolexxxx-xxxx
```

Run below command to verify if all good - 
```
    # expect pods and services from all namespaces will be created.
    kubectl get pods,svc -A
    
    # list all Namespace, verify if the one you configured in cdk.json here.
    kubectl get ns
```


# Build Sample NitroEnclaves App to verify
## Step 1 - Build basic Image
```
   cd test_resource
   bash 01_build_enclave_apps.sh hello
```

After execution, a "hello.eif" will be created under `test_resource/bin/`. This is the encalve app that will be built into another Docker Image in next step.

## Step 2 - Build EIF Image
```
   bash 02_build_eif_image.sh hello
```

After execution, this script will do
  1. Build docker image with EIF inside
  2. Create an ECR repository (if not exists)
  3. Upload the image to ECR repository
  
## Step 3 - Deploy for Docker Image
```
   # check the image location on ECR (from step 2 output)
   # Update below items in the hello_deployment.yaml
   #  - namesapce (align to what cdk.json)
   #  - serviceAccountName (align to what cdk.json)
   #  - `image` under spec.template.spec.containers

   kubectl apply -f hello_deployment.yaml
```

## Step 4 - Verify Output
```
   # Run below command to get pod name, change NS if you customized
   kubectl get pods -n fl
   
   # Get output, this "-f" will keep flowing logs from pod
   kubectl logs -f pod/xxxx -n fl 
   
```