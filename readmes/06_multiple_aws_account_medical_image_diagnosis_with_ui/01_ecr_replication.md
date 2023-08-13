---
title: "步骤 1：设置ECR Replication"
weight: 10
---

> 预计花费时间：10分钟
> 目前的REGION 请选择 US-EAST-1

本章节用于设置 ECR Replication，涉及双方的ECR设置。待设置完成后，`模型技术提供方`的Docker 镜像方可自动复制到 `数据拥有方`的ECR中。 测试双方请按照章节二设置好环境，包括Cloud9，同时请 __
交换双方的`AWS ACCOUNT ID`__，用于后续配置使用。

### 模型技术提供侧配置

1. 在Cloud9环境的命令行中运行以下命令，创建存放预测模型Docker Image的 ECR Repository：<br /><br />

```shell
    aws ecr create-repository --repository-name breast-cancer-classifier --region us-east-1
```

2. 点击下面连接，ECR Repository的 `Private Registry`进行`复制规则`的配置。该配置用于将`breast-cancer-classifier`复制到`数据拥有方`的ECR中。<br /><br />

```shell
   https://us-east-1.console.aws.amazon.com/ecr/private-registry?region=us-east-1
```

3. 点击`Replication configuration` 右侧的`Edit(编辑)` <br /><br />
   ![industryscenario-2-multi-account-tech-p-replication-rule.png](/static/industryscenario-2-multi-account-tech-p-replication-rule.png) <br /><br />


4. 点击`Add Rule` <br /><br />
   ![industryscenario-2-multi-account-tech-p-add-rule.png](/static/industryscenario-2-multi-account-tech-p-add-rule.png) <br /><br />


5. 打开`Cross-account replication`,并关闭`Cross-region replication`, 并点击 `Next` <br /><br />
   ![industryscenario-2-multi-account-tech-p-destination-types.png](/static/industryscenario-2-multi-account-tech-p-destination-types.png) <br /><br />


6. 输入`数据拥有侧的AWS Account ID`，并选择 `us-east-1`（当前测试地区)。点击 `Next` <br /><br />
   ![industryscenario-2-multi-account-tech-p-ca-r.png](/static/industryscenario-2-multi-account-tech-p-ca-r.png) <br /><br />

7. 在Repository filters中输入`breast-cancer-classifier`，并点击`Add`。该值用于限定仅此repo和镜像会被同步复制到对方ECR <br /><br />
   ![industryscenario-2-multi-account-tech-p-repo-filter.png](/static/industryscenario-2-multi-account-tech-p-repo-filter.png) <br /><br />

8. 点击`Submit Rule` <br />

### 数据拥有者侧配置

1. 点击下面连接，ECR Repository的 `Private Registry`进行授权配置。该配置用于允许`模型技术提供方`将`breast-cancer-classifier`复制到本方的ECR中。<br /><br />

```shell
    https://us-east-1.console.aws.amazon.com/ecr/private-registry/permissions?region=us-east-1
```

2. 点击`Generate statement`生成新的permission <br /><br />
   ![industryscenario-2-multi-account-data-o-registry-permission.png](/static/industryscenario-2-multi-account-data-o-registry-permission.png) <br /><br />

3. 按照以下选项进行参数填写，在`Accounts`中填入`模型技术提供方`的AWS Account ID <br /><br />
   ![industryscenario-2-multi-account-data-o-gen-statement.png](/static/industryscenario-2-multi-account-data-o-gen-statement.png) <br /><br />

4. 创建成功后会有如下结果。 <br /><br />
   ![industryscenario-2-multi-account-data-o-gen-statement-result.png](/static/industryscenario-2-multi-account-data-o-gen-statement-result.png)<br /><br />
