---
title: "步骤 3：构建服务器端应用"
weight: 10
---

> 预计花费时间：15分钟
> 目前的REGION 请选择 US-EAST-1

*目前工作坊的使用的人工智能模型为开源模型，可基于公开数据进行训练获得。*

目前使用的乳癌预测模型，其目录机构如下：<br />
![industryscenario-server-breast-cancer-structure.png](/static/industryscenario-server-breast-cancer-structure.png)

1. 在Cloud9 环境的命令行中使用KMS key(`ModelKeyForEnclaves`)对已经人工智能模型进行加密：

```shell

   model_kms_key_arn_id=$(aws kms describe-key --key-id ${MODEL_KEY_ID} | grep "Arn" | perl -p -E "s/((.*)\:\s\")|(\",)//g")

   cd examples/103-breast-cancer-classifier-eks-example/enclaveServer
   pip3 install -r requirements.txt
   python3 ./encrypt_model.py --kms_arn=${model_kms_key_arn_id}
   
   # 将未加密的模型移出构建目录
   mv ./breast_cancer_classifer/models/ImageOnly__ModeImage_weights.p ../
```

2. 开始构建Docker Image

```shell
    #cd 103-breast-cancer-classifier-eks-example/enclaveServer
    docker build -t breast-cancer-classifier:latest .
```

3. 构建服务器端的Enclaves Image File (EIF)

```shell
   nitro-cli build-enclave --docker-uri breast-cancer-classifier:latest --output-file breast-cancer-classifier.eif
```

4. 创建在EKS中运行的Docker image，基于EIF以及配置。

```shell
   docker build -t breast-cancer-classifier:latest_eif -f Dockerfile.eif .
```

*注意事项* <br />
a) 相关的Enclave 配置和 .eif配置的位置请参考 Dockerfile.eif <br />
b) 执行eif 的命令请参考 `run.sh`<br />
c) 在`run.sh`中，使用的是us-east-1，同时开启了 `nitro-cli console` 进行日志的确认和输出。在**实际生产环境中不能开启Console，因为会使得Nitro认证和PCR0在KMS中的使用失效**
。<br />

5. 在cloud9 命令行中，创建 ECR repository（请根据需求改变Region)

```shell
    aws ecr create-repository --repository-name breast-cancer-classifier --region us-east-1 
```

6. 为镜像添加标签，并推送到ECR（请修改ACCOUNT_ID & REGION)

```shell

    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    docker tag breast-cancer-classifier:latest_eif $ACCOUNT_ID.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier:latest_eif
    docker push $ACCOUNT_ID.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier:latest_eif
```

7. 修改部署yaml

```shell
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/breast-cancer-classifier:latest_eif
```

8. 在EKS中运行服务器端应用

```shell
   # Update ~/.kube/config for interacting with EKS
   # This command can be found in CloudFormation >> Output tab
   # aws eks update-kubeconfig --name cluster-eks_enclaves --region <REGION> --role-arn arn:aws:iam::<ACCOUNT_ID>:role/EKS-Enclaves-ClusterAdminRole<SUFFIX>
   
   kubectl apply -f deploy.yaml
```