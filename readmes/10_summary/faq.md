---
title: "FAQ"
weight: 10
---

> 预计花费时间：2分钟 <br/>

### 如何配置跨AWS 账号的KMS 访问（用来实现模型加密/解密） ?

#### 在您账号下 (KEY_USER) - 谁用这个KMS Key

1. At your end, goto IAM page on AWS console.
2. For this demo, the IAM role being used is similar "SSM-access-xxxxx"
3. Click the role
4. Edit the IAM policy - "Allow-EC2Instance-KMS-Encrypt"
5. Add below snippet

```
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

6. Click "Save"

#### 在对方的KMS账号下 (KEY_OWNER) - 谁拥有这个KMS key

1. Locate to remote KMS key (on other account)
2. Get the IAM role from KEY_USER
3. Edit "Key policy" with adding belwo snippet

```
        {
            "Sid": "Allow use of other account",
            "Effect": "Allow",
            "Principal": {
                "AWS": "<ARN_of_IAM_role_from_KEY_USER>"
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
```

4. click "Save"

----