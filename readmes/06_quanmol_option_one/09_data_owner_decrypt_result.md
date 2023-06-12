---
title: "步骤 9: Data Owner解密数据"
weight: 10
---

> 预计花费时间：2分钟
> 目前的REGION 请选择 US-EAST-1

⚠️ *注意事项*

1. __*本步骤在数据拥有者环境中运行*__
2. 本步骤要求数据拥有者环境具备足够权限访问 `S3` 以及`KMS`
3. Step8推理的结果上传到 `QuanMol` S3后，同步复制到`数据拥有者`的S3 bucket（需要提前設置S3
   Replication [Reference Link](https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-walkthrough-2.html))

### 步骤

1. 参考 `utils` 目录下的`end_user_decrypt_data_sample.py`文件，修改line 69 & 70:

```python
bucket_name = "<S3_Bucket_with_Replication_from_TechProvider>"
object_name = "<Encrypted result file name (with prefix)>"
```

2. 安装必要依赖

```shell
pip install -r requirements.txt
```

3. 运行解密

```shell
python3 end_user_decrypt_data_sample.py
```