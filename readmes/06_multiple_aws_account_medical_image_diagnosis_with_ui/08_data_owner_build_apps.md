---
title: "步骤 8：数据拥有方构建客户端以及部署服务端"
weight: 10
---

> 预计花费时间：10分钟
> 目前的REGION 请选择 US-EAST-1

#### 部署服务器端（来自模型技术提供方）

1. 该模型已经通过ECR同步到 `<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/breast-cancer-classifier`中，因此直接部署即可
2. 在examples/103-breast-cancer-classifier-eks-example/enclaveServer目录下，找到`deployment.yaml`
3. 修改第25行, 填入正确的 ACCOUNT_ID and REGION

```shell
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/breast-cancer-classifier:latest_eif
```

4. 部署

```shell
    cd ../enclaveServer
    kubectl apply -f deploy.yaml
```

### 在Cloud9中构建客户端后端程序

1. 构建enclave base Docker image。这个作为Nitro enclave image 的基础镜像。<br/>

```shell
    # location ~/environments/privacy-computing-tee-on-eks
    cd examples/103-breast-cancer-classifier-eks-example-with-ui/
    docker build -t enclave_base .
```

2. 开始构建客户端 Docker Image。本步骤中会构建Client backend app, 包括推送到 Amazon ECR。

```shell
    cd ./enclaveClient
    bash build.sh
```

3. 修改deploy.yaml

```yaml
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/breast-cancer-classifier-client-backend:latest

    # Change line 37, input the S3 bucket that stores images
    - name: IMAGES_S3_BUCKET_LOCATION
      value: "<NEED INPUT>/source"
```

6. 在deploy.yaml确认 REGION是否正确。

```yaml
        env:
          - name: CID
            value: "99999"
          - name: REGION
            value: "us-east-1"
```

7. 部署客户端应用到EKS

```shell
   # Update ~/.kube/config for interacting with EKS
   # This command can be found in CloudFormation >> Output tab
   # 运行eksclusterConfigCommandxxx的值
   # aws eks update-kubeconfig --name cluster-eks_enclaves --region ${REGION} --role-arn arn:aws:iam::${ACCOUNT_ID}:role/EKS-Enclaves-ClusterAdminRolexxxx-xxxx
   kubectl apply -f deploy.yaml
   kubectl apply -f client-svc.yaml
```

### 在Cloud9中构建客户端前端程序

1. 构建enclave base Docker image。这个作为Nitro enclave image 的基础镜像(若已构建，可跳过)<br/>

```shell
    # location ~/environments/privacy-computing-tee-on-eks
    cd examples/103-breast-cancer-classifier-eks-example-with-ui/
    docker build -t enclave_base .
```

2. 开始构建客户端 Docker Image。本步骤中会构建Client frontend app, 包括推送到 Amazon ECR。

```shell
    cd ../enclaveClientFE
    bash build.sh
```

3. 部署前端应用到EKS

```shell
   # Update ~/.kube/config for interacting with EKS
   # This command can be found in CloudFormation >> Output tab
   # 运行eksclusterConfigCommandxxx的值
   # aws eks update-kubeconfig --name cluster-eks_enclaves --region ${REGION} --role-arn arn:aws:iam::${ACCOUNT_ID}:role/EKS-Enclaves-ClusterAdminRolexxxx-xxxx
   kubectl apply -f deploy.yaml
   kubectl apply -f ui-svc.yaml
   kubectl apply -f ingress.yaml
```

4. 部署Ingress 后，请打开Cloud9 terminal, 运行一下命令得到Ingress 的domain name（可能需要等待3-4分钟）

```shell
# After triggered ingress deployment, wait 3-4 mins and check the domain name of INGRESS, with executing
# somthing like : k8s-fl-clientui-xxxxxx-xxxxxx.us-east-1.elb.amazonaws.com
kubectl get ingress -n fl
```

5. 修改deploy.yaml

```yaml
# Change line 43 to ALB domain.
env:
  - name: REACT_APP_ALB_URL
    value: "<Need to update>"
```

6. 重新部署 Frontend deploy

```shell
   kubectl apply -f deploy.yaml
```
