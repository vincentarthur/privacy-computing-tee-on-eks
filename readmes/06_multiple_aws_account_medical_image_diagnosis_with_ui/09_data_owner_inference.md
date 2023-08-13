---
title: "步骤 9：数据方使用图片进行推理"
weight: 10
---

> 预计花费时间：15分钟
> 目前的REGION 请选择 US-EAST-1

以下操作均在 __数据方拥有方__ 的AWS环境和EKS中。

#### 图片准备

1. 将相关需要做处理的图片上传到 S3 bucket（如102-kms-integration创建的bucket)。样例图片在`enclaveClient/images` 可以获取。

```shell
    industry-tee-workshop-${ACCOUNT_ID}-${REGION}-kms-bucket
```

目录结构如下：

```yaml
- s3_bucket
  - source       # use to store source images
  - thumbnails   # use to store thumbnails images. File name should look like "xxxx.png.thumbnail"
```

2. 打开浏览器(新页面), 并输入上一步获得的Application LoadBalancer Domain，会看到类似的以下界面：
   ![industryscenario-2-ui-overview.png](/static/industryscenario-2-ui-overview.png)<br /><br />

3. 选择图片用于预测，并点击 `Predict`, 等待 10-20s,可以获取到预测结果<br /><br />
   ![industryscenario-2-ui-result.png](/static/industryscenario-2-ui-result.png)<br /><br />

#### 后端：服务器端的输出，解密中

4. 等待约1-2分钟，从服务器端可以看到正在进行解密操作 <br />
   ![server-pod-decrypting-log.png](/static/industryscenario-server-pod-decrypting-log.png)

#### 最终服务器端与客户端对于图片的预测输出

5. 服务器端输出 - Log from NitroEnclave (Server) side <br />
   ![server-side-log](/static/industryscenario-server-pod-output.png)
