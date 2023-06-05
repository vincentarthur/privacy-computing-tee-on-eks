---
title: "步骤六：清理"
weight: 10
---

> 预计花费时间：1分钟
> 目前的REGION 请选择 US-EAST-1

本章节需要对刚才资源进行清除，为下一章节做铺垫。

### 清除服务器端作业

1. 清除server pod <br/>

```shell
    cd 102-simple-example/enclavesServer
    kubectl delete -f deploy.yaml
```

### 清除客户端作业

2. 进入到Client 的文件夹并构建镜像

```shell
    # was in 102-simple-example/enclavesServer
    cd ../enclavesClient
    kubectl delete -f deploy.yaml
```