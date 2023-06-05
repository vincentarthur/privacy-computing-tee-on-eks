---
title: "步骤五：Nitro Enclaves与KMS整合"
weight: 10
---

> 预计花费时间：10分钟
> 目前的REGION 请选择 US-EAST-1

本步骤通过整合KMS tool进行安全性的提高，意指在于对IAM role实施KMS访问限制，从而限制程序处理数据的权限（数据使用KMS 进行加密）。 本章节会进行以下步骤：

- 创建AWS KMS Key
- 使用创建的AWS KMS key进行数据的加密
- 重新构建整合KMS访问的 Server & Client docker image
- 部署到EKS进行解密输出<br/>

```shell
    # 请先转换路径到新的章节
    cd ../../102-kmstools-example
```

### 创建S3 bucket

1. 在terminal 中输入, 创建一个用于存放加密数据的S3 bucket.

```shell
   ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
   REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
   bucket_name="industry-tee-solution-workshop-${ACCOUNT_ID}-${REGION}-kms-bucket"
   aws s3 mb ${bucket_name} --region ${REGION}
```

### 创建一个用于加密数据的KMS key (DataKeyForEnclaves)<br />

1. 在命令行运行以下命令进行 KMS Key

```shell
    export REGION=us-east-1

    # Create Key
    DATA_KEY_ID=$(aws kms create-key --description "KMS for Data En/Decryption" --region ${REGION} | grep "KeyId" |perl -p -E "s/((.*)\:\s\")|(\",)//g")
    
    # Create Alias for identification
    aws kms create-alias --alias-name alias/DataKeyForEnclaves --target-key-id ${DATA_KEY_ID}
```

2. 通过以下命令获得KMS Key Policy

```shell
    aws kms get-key-policy --key-id ${DATA_KEY_ID} --policy-name default --output text > DATA_KEY_ID_key_policy.json
```

3. 在Cloud9 以下路径找到`DATA_KEY_ID_key_policy.json` 并双击打开

```text
   102-kmstools-example/DATA_KEY_ID_key_policy.json
```

4. 修改key policy，将以下内容复制并 __覆盖粘贴__ 到DATA_KEY_ID_key_policy.json。 请必须修改第8和16行中的`<ACCOUNT_ID>`为您的AWS账号。

```json
{
  "Version": "2012-10-17",
  "Id": "key-default-1",
  "Statement": [
    {
      "Sid": "Enable IAM User Permissions",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<ACCOUNT_ID>:root"
      },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow use of IRSA",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<ACCOUNT_ID>:role/privacy-computing-eks-irsa"
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    }
  ]
}

```

5. 更新KMS 策略

```shell
    aws kms put-key-policy --policy-name default --key-id ${DATA_KEY_ID} --policy file://DATA_KEY_ID_key_policy.json
```

### 修改 IRSA iam role 权限，加入S3

1. 去到 AWS console， IAM 页面
2. 选择创建的 IRSA role
3. 点击`Create Inline Policy` 如图<br />
   ![image](/static/workshop-step-5_add_s3_permission_irsa.png)<br/>
4. 点击`JSON` tab, 将以下代码覆盖贴入到输入框内并点击`Review Policy`, 请修改"<your-bucket-name>"为您在步骤一创建的Bucket. (可以通过运行 `echo ${bucket_name}`
   得到) <br/>

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAuroraToEncryptedDataBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket",
        "s3:GetObjectVersion",
        "s3:ListMultipartUploadParts"
      ],
      "Resource": [
        "arn:aws:s3:::<your-bucket-name>/*"
      ]
    }
  ]
}
```

5. 输入policy 名称，随意即可,如`s3-bucket-policy-irsa`, 点击`Create Policy`
   <br />

### 创建测试所需加密文件

1. 在terminal运行以下命令生成测试文件，并推送到 S3

```shell
    #cd examples/102-kmstools-example
    
    data_kms_key_arn_id=$(aws kms describe-key --key-id ${DATA_KEY_ID} | grep "Arn" | perl -p -E "s/((.*)\:\s\")|(\",)//g")
    
    bash generate-and-upload-encrypted-data.sh ${bucket_name} ${data_kms_key_arn_id} ${REGION}
    
```

### 构建服务器端镜像

1. 进行Server side image 的构建 <br/>

```shell
    cd 102-simple-example/enclavesServer
    docker build -t simple-ne-server:latest .
```

2. 构建Nitro-Enclave 的EIF(Enclave Image FIle), 这个是最终运行的核心程序

```shell
   nitro-cli build-enclave --docker-uri simple-ne-server:latest --output-file simple-ne-server.eif 
```

3. 创建一个执行层面的Docker Image，并将EIF文件拷贝进去。

```shell
   docker build -t simple-ne-server:latest_eif -f Dockerfile.eif
```

4. 创建一个ECR repository，用于存放镜像 (如果101 执行过可以跳过此步骤)

```shell
    aws ecr create-repository --repository-name simple-ne-server --region ${REGION}
```

5. 进行镜像的标签以及推送

```shell
    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    docker tag simple-ne-server:latest_eif ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/simple-ne-server:latest_eif 
    docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/simple-ne-server:latest_eif
```

6. 修改`deploy.yaml` 第25行，将Image 的路径改成上述路径

```yaml
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/simple-ne-server:latest_eif
```

7. 部署Server app 到EKS, 请参考部署输出的EKS command 进行 k8s config更新。

```shell
   # Update ~/.kube/config for interacting with EKS
   # This command can be found in CloudFormation >> Output tab
   # aws eks update-kubeconfig --name cluster-eks_enclaves --region ${REGION} --role-arn arn:aws:iam::${ACCOUNT_ID}:role/EKS-Enclaves-ClusterAdminRole<SUFFIX>
   
   kubectl apply -f deploy.yaml
```

8. 查看Server log output（需要等待pod launch)

```shell
   kubectl get pods -n fl # you can find a pod name like "server-xxxx-xxxx" # target is RUNNING status
   kubectl logs -f -l app=server -n fl
```

![image](/static/workshop-step-5_server_output.png) <br />

### 构建客户端镜像

9. 进入到Client 的文件夹并构建镜像

```shell
    # was in 102-simple-example/enclavesServer
    cd ../enclavesClient
    docker build -t simple-ne-client:latest .
```

10. 创建 ECR Repository (如果101 执行过可以跳过此步骤)

```shell
    aws ecr create-repository --repository-name simple-ne-client --region ${REGION}
```

11. 打标签推送

```shell
    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    docker tag simple-ne-client:latest ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/simple-ne-client:latest
    docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/simple-ne-client:latest
```

12. 修改`deploy.yaml`的以下参数

```yaml
     env:
       - name: CID
         value: "99999"
       - name: ENCRYPTED_DATA_S3_URI
         value: "s3://<your-bucket-name>/encrypted_data.txt"   # sample s3 uri of encrypted data
       - name: REGION
         value: "us-east-1" #按需修改
```

13. 部署到EKS

```shell
   kubectl apply -f deploy.yaml
```

----

#### 查看日志

通过运行以下命令可以查看客户端的日志和执行结果 <br/>

```shell
   kubectl get pods -n fl # you can find a pod name like "client-xxxx-xxxx"
   kubectl logs -f -l app=client -n fl
```

看到如以下结果<br/>

```shell
   Received msg from Server: {"decoded_message": "example-encrypted-text"}
```

![image](/static/workshop-step-5_client-received-response.png)