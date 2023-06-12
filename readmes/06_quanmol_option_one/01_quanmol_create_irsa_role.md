---
title: "步骤 1: QuanMol创建IRSA"
weight: 10 
---

> 预计花费时间：5分钟
> 目前的REGION 请选择 US-EAST-1

### 创建IRSA role

创建一个IAM role 用于在EKS中运行，并且访问`药物研发`的KMS，用于在Nitro Enclave中解密数据。 <br />

```
https://us-east-1.console.aws.amazon.com/iamv2/home?region=us-east-1#/roles
```

点击右上角"Create Role". <br/>
![Create Role](/static/prerequisite-step-1-iam-role.png)

然后如下图： <br/>

1) 选择`AWS Service` 作为 *"Trusted Entity Type"*
2) 选择`EC2`作为 *"Common Use Cases"*.
3) 点击 `Next`.<br/>

![Trusted Entity](/static/prerequisite-step-1-iam-role-2.png)

4) 在 "Add Permissions" 页面中，点击 `Create Policy`, 页面会自动跳转至新页面。<br/>

![Create Policy](/static/workshop-step-1-irsa-1.png)<br/>

5) 点击`JSON` tab,如下图：<br/>
   ![Create Policy](/static/workshop-step-1-irsa-2.png)<br/>

6) 在输入框中内容全部替换成一下内容:<br/>

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:DescribeVolumesModifications",
        "ecr:ListTagsForResource",
        "ecr:ListImages",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DescribeVolumes",
        "ecr:DescribeRepositories",
        "ec2:UnassignPrivateIpAddresses",
        "ec2:DescribeRouteTables",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetLifecyclePolicy",
        "ecr:DescribeImageScanFindings",
        "ec2:DetachNetworkInterface",
        "ecr:GetLifecyclePolicyPreview",
        "ec2:DescribeTags",
        "ecr:GetDownloadUrlForLayer",
        "ec2:ModifyNetworkInterfaceAttribute",
        "ec2:DeleteNetworkInterface",
        "ecr:GetAuthorizationToken",
        "ec2:AssignPrivateIpAddresses",
        "ec2:DescribeSecurityGroups",
        "ec2:CreateNetworkInterface",
        "ec2:DescribeVpcs",
        "ecr:BatchGetImage",
        "ecr:DescribeImages",
        "ec2:DescribeInstanceTypes",
        "eks:DescribeCluster",
        "ec2:AttachNetworkInterface",
        "ec2:DescribeSubnets",
        "ecr:GetRepositoryPolicy"
      ],
      "Resource": "*"
    },
    {
      "Sid": "VisualEditor1",
      "Effect": "Allow",
      "Action": "ec2:CreateTags",
      "Resource": "arn:aws:ec2:*:*:network-interface/*"
    }
  ]
}
```

7) 点击 `Next: Tags`,接着点击 `Next: Review`
8) 输入 策略名字 (例如: `privacy-computing-eks-irsa-policy`)
9) 点击 `Create Policy`
10) 回到步骤#4，在搜索栏中输入 `privacy-computing-eks-irsa-policy`, 勾选，点击 `Next`
11) 输入IAM Role 名称 (比如 `privacy-computing-eks-irsa-role`), 点击`Create Role`.



