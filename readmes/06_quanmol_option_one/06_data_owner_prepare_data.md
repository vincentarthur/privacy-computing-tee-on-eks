---
title: "步骤 6: 数据方加密图片"
weight: 10
---

> 预计花费时间：15分钟
> 目前的REGION 请选择 US-EAST-1

以下操作在 __数据方拥有方__ 的AWS环境中。

#### 客户端应用
1. 进入客户端应用后，做以下步骤: <br />
   a) 使用KMS 对图片进行加密（已经预先放入了测试图片）<br />
   b) 想服务器端发起图片分析请求 <br />

```shell
   cd /app
   
   ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
   REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    
   #a - Encrypt the prepared image
   export AWS_DEFAULT_REGION=$REGION
   python3 ./encryptor.py --filePath ./0_L_CC.png --cmkId alias/DataKeyForEnclaves --region $AWS_DEFAULT_REGION   
   # Verify that the output contains: file encrypted? True
   
   # Push data to QuanMol S3 bucket
   aws s3 cp 0_L_CC.png.encrypted s3://<QUANMOL_S3_BUCKET>
```