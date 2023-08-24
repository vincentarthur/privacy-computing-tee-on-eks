---
title: "步骤 5：模型技术提供方加密模型并构建Docker Image"
weight: 10
---

> 预计花费时间：40分钟
> 目前的REGION 请选择 US-EAST-1

*目前工作坊的使用的人工智能模型为开源模型，可基于公开数据进行训练获得。*

目前使用的乳癌预测模型，其目录机构如下：<br />
![industryscenario-server-breast-cancer-structure.png](/static/industryscenario-server-breast-cancer-structure.png)

1. 在Cloud9命令行中下载代码, 并进入模型构建目录 <br /><br />

```shell
    git clone https://github.com/vincentarthur/privacy-computing-tee-on-eks.git
    
    cd privacy-computing-tee-on-eks/examples/103-breast-cancer-classifier-eks-example-with-ui/
```

2. 构建enclave base Docker image。这个作为Nitro enclave image 的基础镜像。<br/>

```shell
    docker build -t enclave_base .
```

3. 在Cloud9 环境的命令行中使用KMS key(`ModelKeyForEnclaves`)对已经人工智能模型进行加密： <br /><br />

```shell

   model_kms_key_arn_id=$(aws kms describe-key --key-id ${MODEL_KEY_ID} | grep "Arn" | perl -p -E "s/((.*)\:\s\")|(\",)//g")

   cd enclaveServer
#   pip3 install -r requirements.txt
   python3 ./encrypt_model.py --kms_arn=${model_kms_key_arn_id}
   
   # 将未加密的模型移出构建目录
   mv ./breast_cancer_classifier/models/ImageOnly__ModeImage_weights.p ../
```

2. 开始构建Docker Image <br /><br />

```shell
    #cd 103-breast-cancer-classifier-eks-example/enclaveServer
    docker build -t breast-cancer-classifier:latest .
```

3. 构建服务器端的Enclaves Image File (EIF) <br /><br />

```shell
   sudo nitro-cli build-enclave --docker-uri breast-cancer-classifier:latest --output-file breast-cancer-classifier.eif
```

当构建完成，会看到3个PCR值，请记下，后续需要用于 KMS Policy配置。 <br /><br />
![incustryscenario-2-multi-account-pcrs.png](/static/incustryscenario-2-multi-account-pcrs.png)

4. 创建在EKS中运行的Docker image，基于EIF以及配置。 <br /><br />

```shell
   docker build -t breast-cancer-classifier:latest_eif -f Dockerfile.eif .
```

*注意事项* <br />
a) 相关的Enclave 配置和 .eif配置的位置请参考 Dockerfile.eif <br />
b) 执行eif 的命令请参考 `run.sh`<br />
c) 在`run.sh`中，使用的是us-east-1，同时开启了 `nitro-cli console` 进行日志的确认和输出。在**实际生产环境中不能开启Console，因为会使得Nitro认证和PCR0在KMS中的使用失效**
。<br />

5. 为镜像添加标签，并推送到ECR（请修改ACCOUNT_ID & REGION)

```shell
    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    docker tag breast-cancer-classifier:latest_eif ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier:latest_eif
    docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier:latest_eif
```

6. 检查ECR 镜像推送是否同步成功 <br />
   a) 打开以下链接进入ECR <br />

```
https://us-east-1.console.aws.amazon.com/ecr/repositories/private/
```    

b) 点击 `breast-cancer-classifier` repository <br />
c) 点击 Image tag - `latest_eif` <br />
d) 在 `Replication Status` 检查是否有成功的条目，如下图 <br /><br />
![industryscenario-2-multi-account-replication-pass.png](/static/industryscenario-2-multi-account-replication-pass.png)

