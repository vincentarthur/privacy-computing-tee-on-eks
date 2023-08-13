---
title: "步骤 4：模型技术提供方创建用于加解密模型的KMS Key"
weight: 10
---

> 预计花费时间：10分钟
> 目前的REGION 请选择 US-EAST-1

#### 模型技术提供方 - 创建一个用于加密解密的KMS key (ModelKeyForEnclaves) <br /><br />

1. 在命令行运行以下命令进行 KMS Key <br />

```shell

    export REGION=us-east-1
    
    # Create Key
    MODEL_KEY_ID=$(aws kms create-key --description "KMS for Model En/Decryption" --region ${REGION} | grep "KeyId" |perl -p -E "s/((.*)\:\s\")|(\",)//g")
    
    # Create Alias for identification
    aws kms create-alias --alias-name alias/ModelKeyForEnclaves --target-key-id ${MODEL_KEY_ID}
```

2. 通过以下命令获得KMS Key Policy <br />

```shell
    aws kms get-key-policy --key-id ${MODEL_KEY_ID} --policy-name default --output text > MODEL_KEY_ID_key_policy.json
```

3. 在Cloud9 以下路径找到`MODEL_KEY_ID_key_policy.json` 并双击打开 <br />

```text
   103-breast-cancer-classifier-eks-example/MODEL_KEY_ID_key_policy.json
```

4. 修改key policy，将以下内容复制并 __覆盖粘贴__ MODEL_KEY_ID_key_policy.json。 <br />
   a) 请修改第8行中的`<ACCOUNT_ID>`为您的AWS账号。 <br />
   b) 请修改第16行中的`<ACCOUNT_ID>`为 __数据拥有方__ 的AWS账号。 <br />

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
            "AWS": "arn:aws:iam::<ACCOUNT_ID>:role/privacy-computing-eks-irsa-role"
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

5. 在Cloud9命令行中运行以下命令更新KMS策略。策略更新成功后，数据方的 IAM role `privacy-computing-eks-irsa-role`能访问此KMS可以对模型进行解密。

```shell
    aws kms put-key-policy --policy-name default --key-id ${MODEL_KEY_ID} --policy file://MODEL_KEY_ID_key_policy.json
```