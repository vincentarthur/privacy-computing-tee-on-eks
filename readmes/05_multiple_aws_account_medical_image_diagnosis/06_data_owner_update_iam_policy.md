---
title: "步骤 6: 数据拥有方更新IAM role policy"
weight: 10
---

> 预计花费时间：5分钟
> 目前的REGION 请选择 US-EAST-1

本步骤需要对`IRSA`的IAM Policy进行修改，授权访问`模型技术提供方`的KMS Key(`ModelKeyForEnclaves`)，用于解密模型。<br />
__这一步骤需要向`模型技术提供方`索要`ModelKeyForEnclaves` KMS的ARN ID。__ <br /><br />

1. 打开以下链接跳转至之前创建的IRSA Policy

```
https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/policies/details/arn%3Aaws%3Aiam%3A%3A115033083588%3Apolicy%2Fprivacy-computing-eks-irsa-policy?section=policy_permissions
```

2. 点击Edit <br /><br />
   ![industryscenario-2-multi-account-data-o-iam-p-add.png](/static/industryscenario-2-multi-account-data-o-iam-p-add.png) <br /><br />

3. 将以下内容 __追加__ 到Policy中。请替换`ARN`为 `模型技术提供方`的`ModelKeyForEnclaves`KMS的ARN ID<br/>

```json
        {
            "Sid": "AllowExternalKMSAccess",
            "Effect": "Allow",
            "Action": [
                "kms:Encrypt",
                "kms:Decrypt",
                "kms:ReEncrypt*",
                "kms:GenerateDataKey*",
                "kms:DescribeKey"
            ],
            "Resource": "<ARN_of_KMS_key_from_other_account>"
        }
```

4. 点击`Next` -> `Save Change`


