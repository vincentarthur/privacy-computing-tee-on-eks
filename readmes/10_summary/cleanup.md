---
title: "清除资源"
weight: 10
---

> 预计花费时间：20分钟
> 目前的REGION 请选择 US-EAST-1

与建立资源相似，在命令行上运行以下命令：
```shell
cdk destroy --all --require-approval never
```

期间会遇到以下的问题：<br />
![Clean Up Error](/static/cleanup-error.png)<br />

其原因是在自动创建的IAM role上加入了SSM 的权限，请参考在IAM 页面上进行手动删除后，等待上述command 失败后重新执行即可。<br/>
![Clean SSM](/static/cleanup-iam-ssm-issue.png)

清理完成如下图：<br />
![Clean Up OK](/static/cleanup-success.png)


