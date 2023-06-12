---
title: "步骤 4: 数据拥有方创建用于加密数据的KMS Key"
weight: 10
---

> 预计花费时间：10分钟
> 目前的REGION 请选择 US-EAST-1

#### 数据拥有方配置 - 创建一个用于数据的KMS key (DataKeyForEnclaves) <br /><br />

1. 在命令行运行以下命令进行 KMS Key <br />

```shell
    export REGION=us-east-1

    # Create Key
    DATA_KEY_ID=$(aws kms create-key --description "KMS for Data En/Decryption" --region ${REGION} | grep 'KeyId' | perl -p -E "s/((.*)\:\s\")|(\",)//g")
    
    # Create Alias for identification
    aws kms create-alias --alias-name alias/DataKeyForEnclaves --target-key-id ${DATA_KEY_ID}
```

2. 通过以下命令获得KMS Key Policy

```shell
    aws kms get-key-policy --key-id ${DATA_KEY_ID} --policy-name default --output text > DATA_KEY_ID_key_policy.json
```

3. 在Cloud9 以下路径找到`DATA_KEY_ID_key_policy.json` 并双击打开

```text
   DATA_KEY_ID_key_policy.json
```

4. 修改key policy，将以下内容复制并 __覆盖粘贴__ 到DATA_KEY_ID_key_policy.json。<br />
   请必须修改第8行中的`<ACCOUNT_ID>`为数据拥有方AWS账号。 <br />
   请必须修改第16行中的`<QUANMOL_ACCOUNT_ID>`为QuanMolAWS账号。 <br />
   请必须修改第31行中的`<ARN_IAM_ROLE>`为数据拥有方用于 __推送数据的IAM Role arn__ 。 <br />
   __注意空格对齐__。

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
        "AWS": "arn:aws:iam::<QUANMOL_ACCOUNT_ID>:role/privacy-computing-eks-irsa-role"
      },
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:DescribeKey"
      ],
      "Resource": "*"
    },
    {
      "Sid": "Allow use of Data Owner's IAM",
      "Effect": "Allow",
      "Principal": {
        "AWS": "ARN_IAM_ROLE"
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

5. 在Cloud9命令行中运行以下命令更新KMS策略。策略更新成功后，IAM role `privacy-computing-eks-irsa-role`能访问KMS可以对数据进行解密。

```shell
    aws kms put-key-policy --policy-name default --key-id ${DATA_KEY_ID} --policy file://DATA_KEY_ID_key_policy.json
```