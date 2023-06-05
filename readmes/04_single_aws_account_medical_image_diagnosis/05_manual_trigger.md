---
title: "步骤 5：与客户端、服务器端交互"
weight: 10
---

> 预计花费时间：15分钟
> 目前的REGION 请选择 US-EAST-1

本章节我们通过交互的方式实际体验一下服务器端和客户端的应用的运行情况。 __实际生产环境不能直接访问。__

#### 服务器端应用

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

#### 客户端应用

3. 开一个新的Cloud9命令行窗口，以相同的方式进入客户端应用

```shell
   kubectl get pods -n fl # you can find a pod name like "client-xxxx-xxxx"
   kubectl exec -it pod/client-xxxx -n fl -- /bin/bash
```

4. 进入客户端应用后，做以下步骤: <br />
   a) 使用KMS 对图片进行加密（已经预先放入了测试图片）<br />
   b) 想服务器端发起图片分析请求 <br />

```shell
   cd /app
   
   #a - Encrypt the prepared image
   export AWS_DEFAULT_REGION=$REGION
   python3 ./encryptor.py --filePath ./0_L_CC.png --cmkId alias/DataKeyForEnclaves --region $AWS_DEFAULT_REGION
   
   # Verify that the output contains: file encrypted? True
   
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