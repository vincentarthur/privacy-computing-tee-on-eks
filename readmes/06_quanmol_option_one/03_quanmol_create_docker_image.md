---
title: "步骤 3: QuanMol 构建Server Side Docker Image"
weight: 10
---

> 预计花费时间：40分钟
> 目前的REGION 请选择 US-EAST-1

*目前工作坊的使用的人工智能模型为开源模型，可基于公开数据进行训练获得。*

目前使用的乳癌预测模型，其目录机构如下：<br />
![industryscenario-server-breast-cancer-structure.png](/static/industryscenario-server-breast-cancer-structure.png)

### 构建服务器端程序

1. 在Cloud9命令行中下载代码, 并进入模型构建目录 <br/>
   ⚠️ 注意: `103-breast-cancer-classifier-eks-example-2` 比 `103-breast-cancer-classifier-eks-example`多了对于以下内容 <br/>
    - 使用KMS key加密推理结果
    - 上传加密数据到QuanMol S3 bucket
    - 样例代码用于解密数据(运行在数据拥有方)

```shell
    git clone https://github.com/vincentarthur/privacy-computing-tee-on-eks.git
    
    cd privacy-computing-tee-on-eks/examples/103-breast-cancer-classifier-eks-example-2/
```

2. 构建enclave base Docker image。这个作为Nitro enclave image 的基础镜像。<br/>

```shell
    docker build -t enclave_base .
```

3. 开始构建Docker Image <br />

```shell
    cd examples/103-breast-cancer-classifier-eks-example-2/enclaveServer
    docker build -t breast-cancer-classifier:latest .
```

4. 构建服务器端的Enclaves Image File (EIF) <br /><br />

```shell
   sudo nitro-cli build-enclave --docker-uri breast-cancer-classifier:latest --output-file breast-cancer-classifier.eif
```

⚠️⚠️⚠️ 构建完成后会看到3个PCR值，请记下，后续`药物研发机构`需要用于 KMS Policy配置。 <br /><br />
![incustryscenario-2-multi-account-pcrs.png](/static/incustryscenario-2-multi-account-pcrs.png)

5. 创建在EKS中运行的Docker image，基于EIF以及配置。 <br /><br />

```shell
   docker build -t breast-cancer-classifier:latest_eif -f Dockerfile.eif .
```

*注意事项* <br />
a) 相关的Enclave 配置和 .eif配置的位置请参考 Dockerfile.eif <br />
b) 执行eif 的命令请参考 `run.sh`<br />
c) 在`run.sh`中，使用的是us-east-1，同时开启了 `nitro-cli console` 进行日志的确认和输出。在**实际生产环境中不能开启Console，因为会使得Nitro认证和PCR0在KMS中的使用失效**
。<br />

6. 为镜像添加标签，并推送到ECR（请修改ACCOUNT_ID & REGION)

```shell
    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    docker tag breast-cancer-classifier:latest_eif ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier:latest_eif
    docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier:latest_eif
```

7. 修改``修改第25行, 填入正确的 ACCOUNT_ID and REGION

```shell
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/breast-cancer-classifier:latest_eif
```

8. 部署

```shell
    cd ../enclaveServer
    kubectl apply -f deploy.yaml
```

### 构建客户端程序

1. 开始构建客户端 Docker Image

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
    docker tag breast-cancer-classifier-client:latest ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier-client:latest
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
          - name: RESULT_UPLOAD_BUCKET
            value: <Input S3 for storing encrypted result>
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
