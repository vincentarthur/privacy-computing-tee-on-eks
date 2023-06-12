---
title: "步骤 2: 设置S3"
weight: 10 
---

> 预计花费时间：10分钟
> 目前的REGION 请选择 US-EAST-1

本章节用于设置`QuanMol` 以及`药物研发机构`的S3, 包括

- `药物研发机构`创建用于推送加密数据到`QuanMol`的IAM role
- `QuanMol`创建用于存储来自`药物研发机构`的加密数据, 并授权`药物研发机构`IAM访问权限

### 药物研发机构创建 IAM Role

该IAM role 需要被使用在EC2 instance上进行

- 蛋白质数据的加密 （访问KMS key生成加密密钥）
- 推送数据到`QuanMol` S3

```
https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/roles
```

点击右上角"Create Role". <br/>
![Create Role](/static/prerequisite-step-1-iam-role.png)

然后如下图： <br/>

1) 选择`AWS Service` 作为 *"Trusted Entity Type"*
2) 选择`EC2`作为 *"Common Use Cases"*.
3) 点击 `Next`.<br/>

![Trusted Entity](/static/prerequisite-step-1-iam-role-2.png)<br/>

4) 在 "Add Permissions" 页面中，点击 `Create Policy`, 页面会自动跳转至新页面。<br/>
   ![Create Policy](/static/workshop-step-1-irsa-1.png)<br/>

5) 点击`JSON` tab,如下图：<br/>
   ![Create Policy](/static/workshop-step-1-irsa-2.png)<br/>

6) 在输入框中内容全部替换成一下内容(可根据需要调整`Actions` and `Resource`):<br/>

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "kms:*"
      ],
      "Resource": "*"
    }
  ]
}
```

7) 点击 `Next: Tags`,接着点击 `Next: Review`
8) 输入策略名字 (例如: `data-owner-iam-policy`)
9) 点击 `Create Policy`
10) 回到步骤#4，在搜索栏中输入 `data-owner-iam-policy`, 勾选，点击 `Next`
11) 输入IAM Role 名称 (比如 `data-owner-iam-role`), 点击`Create Role`.
12) 在页面上复制`ARN`的值，并 __分享到`QuanMol`__

### QuanMol 创建 S3

1. 在Cloud9环境的命令行中运行以下命令，创建用于接收`药物研发机构的加密数据`：<br /><br />

```shell
    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    
    BUCKET_NAME="customer-encrypted-data-${ACCOUNT_ID}-${REGION}"
    
    aws s3 mb s3://${BUCKET_NAME} --region ${REGION}
```

2. 授权`药物研发机构`IAM role对QuanMol S3 Bucket写权限，授权IRSA role S3所有权限。（按需修改）

- 修改`ARN_OF_EXTERNAL_IAM_ROLE`为`药物研发机构`创建的IAM role
- 修改`QUANMOL_S3_BUCKET`为上一步骤创建的bucket名称
- 修改`QUANMOL_ACCOUNT_ID`为QuanMol AWS Account ID
- 并保存为`bucket_policy.json`

```json
{
  "Version": "2012-10-17",
  "Id": "PutObjPolicy",
  "Statement": [
    {
      "Sid": "AllowPutObject",
      "Principal": {
        "AWS": "ARN_OF_EXTERNAL_IAM_ROLE"
      },
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::QUANMOL_S3_BUCKET/*"
    },
    {
      "Sid": "AllowAllActionObject",
      "Principal": {
        "AWS": "arn:aws:iam::QUANMOL_ACCOUNT_ID:role/privacy-computing-eks-irsa-role"
      },
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::QUANMOL_S3_BUCKET/*"
    }
  ]
}
```

3. 执行更新Bucket Policy

```shell
   aws s3api put-bucket-policy --bucket ${BUCKET_NAME} --policy file://bucket_policy.json
```
