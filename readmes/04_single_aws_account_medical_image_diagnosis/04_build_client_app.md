---
title: "步骤 4：构建客户端应用"
weight: 10
---

> 预计花费时间：15分钟
> 目前的REGION 请选择 US-EAST-1

1. 在Cloud9 环境的命令行构建客户端应用：

```shell
    cd ../enclaveClient
    # Current location should be "103-breast-cancer-classifier-eks-example/enclaveClient"
    docker build -t breast-cancer-classifier-client:latest .
```

2. 在cloud9 命令行中，创建 ECR repository（请根据需求改变Region)

```shell
    aws ecr create-repository --repository-name breast-cancer-classifier-client --region us-east-1
```

3. 为镜像添加标签，并推送到ECR（请修改ACCOUNT_ID & REGION)

```shell
    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    docker tag breast-cancer-classifier-client:latest $ACCOUNT_ID.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier-client:latest
    docker push $ACCOUNT_ID.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier-client:latest
```

4. 修改deploy.yaml

```shell
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/breast-cancer-classifier-client:latest
```

5. 在deploy.yaml确认 REGION是否正确。

```yaml
        env:
          - name: CID
            value: "99999"
          - name: REGION
            value: "us-east-1"
```

6. 部署客户端应用到EKS

```shell
   # Update ~/.kube/config for interacting with EKS
   # This command can be found in CloudFormation >> Output tab
   # 运行eksclusterConfigCommandxxx的值
   # aws eks update-kubeconfig --name cluster-eks_enclaves --region ${REGION} --role-arn arn:aws:iam::${ACCOUNT_ID}:role/EKS-Enclaves-ClusterAdminRolexxxx-xxxx
   kubectl apply -f deploy.yaml
```