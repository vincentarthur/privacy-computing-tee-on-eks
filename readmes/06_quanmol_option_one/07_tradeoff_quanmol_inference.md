---
title: "步骤 7: `临时TradeOff` QuanMol触发数据分析和推理"
weight: 10
---
本章节目前使用`Workaround Solution`来触发数据分析和推理，因为暂时没有构建前端页面。<br />
*最终预期效果为用户通过前端页面输入文件在`QuanMol S3的路径`来触发分析和推理。*

### 启动服务器端程序

*目前使用手动方式触发以便更好理解整体流程，实际生产环境可以通过修改`Docker_file.eif`中的`CMD`来实现自动启动。*

1. 在Cloud9 环境的命令行中运行以下命令，进入到服务器端的应用：

```shell

    # 您會看到名如 "server-xxxx-xxxx"的pod
    # 请记下您所选pod 对应的node 名字（因为一会需要选择同一节点对应的客户端应用）
    kubectl get pods -n fl -o wide 
    
    # 进入服务器端应用
    kubectl exec -it pod/server-xxxx -n fl -- /bin/bash
```

2. 当进入服务器端应用后，运行一下命令启动Nitro Enclave Image File

```shell
   cd /app
   bash run.sh
   
   # then wait 1-2 mins, you will see similar log as below
```

![server-side-log](/static/industryscenario-server-pod-initializing.png)

### Workaround Solution 介紹

此workaround solution为：QuanMol进入 EKS client pod，并将加密数据推送到Server Pod(`Nitro Enclaves`)中进行处理。

1. 开一个新的Cloud9命令行窗口，以相同的方式进入客户端应用

```shell
   kubectl get pods -n fl # you can find a pod name like "client-xxxx-xxxx"
   kubectl exec -it pod/client-xxxx -n fl -- /bin/bash
```

2. 通过命令行下载加密数据并送往Server pod进行解密和推理。请替换`quanmol_encrypted_data_s3_bucket`为实际存储加密数据的S3 bucket name<br />

```shell
   cd /app
   
   ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
   REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
   BUCKET_NAME="<quanmol_encrypted_data_s3_bucket>"
   
   #a - Download file
   aws s3 cp s3://${BUCKET_NAME}/0_L_CC.png.encrypted .
    
   #b - Trigger the classification and model decryption
   python3 client.py --filePath ./0_L_CC.png.encrypted
```

#### 观察服务器端的输出，解密中

5. 等待约1-2分钟，从服务器端可以看到正在进行解密操作 <br />
   ![server-pod-decrypting-log.png](/static/industryscenario-server-pod-decrypting-log.png)

#### 最终服务器端与客户端对于CT图片的预测输出

6. 服务器端输出 - Log from NitroEnclave (Server) side <br />
   ![server-side-log](/static/industryscenario-server-pod-output.png)


7. 客户端输出 - Log from Client side <br />
   ![client-side-log](/static/industryscenario-client-pod-output.png)