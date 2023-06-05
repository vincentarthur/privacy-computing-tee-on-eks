---
title: "步骤 1：构建基础Docker镜像"
weight: 10
---

> 预计花费时间：10分钟
> 目前的REGION 请选择 US-EAST-1

1. 在Cloud9 环境的命令行中运行：

```shell
cd examples/103-breast-cancer-classifier-eks-example
```

2. 进行初始Docker image构建，这个是作为Nitro enclave image 的基础镜像。如果已经执行过 "Hello World" 测试，此步骤可跳过。<br/>

```shell
docker build -t enclave_base .
```