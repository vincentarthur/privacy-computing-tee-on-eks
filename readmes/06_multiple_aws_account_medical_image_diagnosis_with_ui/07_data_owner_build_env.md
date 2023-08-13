---
title: "步骤 7：数据拥有方构建环境"
weight: 10
---

> 预计花费时间：40分钟
> 目前的REGION 请选择 US-EAST-1

*目前工作坊的使用的人工智能模型为开源模型，可基于公开数据进行训练获得。*

目前使用的乳癌预测模型，其目录机构如下：<br />
![industryscenario-server-breast-cancer-structure.png](/static/industryscenario-server-breast-cancer-structure.png)

### 在Cloud9 环境中按步骤执行

1. 安装kubectl/eksctl/cdk2

```shell
   cd privacy-computing-tee-on-eks
   bash utils_scripts/00_install_kubectl_eksctl.sh
   
   npm install -g aws-cdk@latest
   
   # 如果上述命令遇到error 请运行一下命令
   npm install -g aws-cdk@latest --force
```

2. 创建并准备python 虚拟环境

```shell
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install -r requirements.txt
   
   ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
   REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
   
   # 准备CDK 环境
   ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
   cdk bootstrap aws://${ACCOUNT_ID}/${REGION}
```

3. 在Cloud9命令行中下载代码, 并进入目录 <br /><br />

```shell
    git clone https://github.com/vincentarthur/privacy-computing-tee-on-eks.git
    
    cd privacy-computing-tee-on-eks/
```

4. 修改cdk.json。 在cdk.json中将正确的`AWS ACCOUNT ID`填入第8行, 并保存

```json
"ACCOUNT_ID": "xxxxxxxx",
"REGION": "us-east-1",
```

5. 部署EKS

```shell
    bash 01_install.sh
```

![img.png](/static/workshop-step-3-wip.png) <br /><br />

6. 当看到以下类似信息打印在命令行，则表示部署完成。请复制 `EKS-Enclaves.eksclusterConfigCommandxxx`的值（到.txt)，后续步骤需要*_多次_*使用。 <br /><br />
   ![image.png](/static/workshop-step-3-deploy-success.png) <br /><br />

7. 进行IRSA在EKS cluster上的配置。 <br /><br />

```shell
    # cluster-eks_enclaves为集群名字，如需修改可在上一步骤中进行
    bash 02_setup_irsa.sh cluster-eks-enclaves
```

![image.png](/static/workshop-step-3-deploy-irsa.png)<br/>

8. 验证EKS and Nitro Enclaves是否部署成功<br/>

```shell
  # 首先在 Cloud9 控制台中输入类似的命令
  # 改命令请参考步骤4 的输出
  ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
  REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
  
  # 运行eksclusterConfigCommandxxx的值（步骤4）
  aws eks update-kubeconfig --name cluster-eks_enclaves --region ${REGION} --role-arn arn:aws:iam::${ACCOUNT_ID}:role/EKS-Enclaves-ClusterAdminRolexxxx-xxxx

  # 查询所有的节点、pod 以及namespace
  kubectl get nodes,pods,ns -A
```

![Images](/static/workshop-step-3-res-output.png)<br/>
