---
title: "步骤 8：数据拥有方构建客户端以及部署服务端"
weight: 10
---

> 预计花费时间：10分钟
> 目前的REGION 请选择 US-EAST-1

### 在Cloud9中构建客户端程序

1. 构建enclave base Docker image。这个作为Nitro enclave image 的基础镜像。<br/>

```shell
    # location ~/environments/privacy-computing-tee-on-eks
    cd examples/103-breast-cancer-classifier-eks-example/
    docker build -t enclave_base .
```

2. 开始构建客户端 Docker Image
```shell
    cd ../enclaveClient
    # Current location should be "103-breast-cancer-classifier-eks-example/enclaveClient"
    docker build -t breast-cancer-classifier-client:latest .
```

3. 在cloud9 命令行中，创建 ECR repository（请根据需求改变Region)

```shell
    aws ecr create-repository --repository-name breast-cancer-classifier-client --region us-east-1
```

4. 为镜像添加标签，并推送到ECR（请修改ACCOUNT_ID & REGION)

```shell
    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    docker tag breast-cancer-classifier-client:latest ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier-client:latest
    docker push $ACCOUNT_ID.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier-client:latest
```

5. 修改deploy.yaml

```shell
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/breast-cancer-classifier-client:latest
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
```

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