---
title: "步骤四：部署Hello World"
weight: 10
---

> 预计花费时间：20分钟
> 目前的REGION 请选择 US-EAST-1

本步骤通过构建简单的Hello World 程序并且部署到EKS nitro enclaves 的节点上快速进行测试。 Nitro Enclave application 其实是 Server-Client
的模式，可以在服务器端或者客户端运行Nitro Enclaves，目前的样例是服务器端运行NitroEnclave，而通过客户端进行交互。<br/>

1. 在命令行中运行以下命令进行Nitro Enclave基础镜像构建。此基础景象会作为后续构建Nitro Enclave应用的基础，被多次使用。 <br/>

``` shell
cd examples/101-simple-example
docker build -t enclave_base .
```

### 构建服务器端镜像

3. 当构建完#2 image 后，进行Server side image 的构建 <br/>

```shell
    cd 101-simple-example/enclavesServer
    docker build -t simple-ne-server:latest .
```

4. 构建Nitro-Enclave 的EIF(Enclave Image FIle), 这个是最终运行的核心程序

```shell
   nitro-cli build-enclave --docker-uri simple-ne-server:latest --output-file simple-ne-server.eif 
```

5. 创建一个执行层面的Docker Image，并将EIF文件拷贝进去。

```shell
   docker build -t simple-ne-server:latest_eif -f Dockerfile.eif .
```

6. 创建一个ECR repository，用于存放镜像

```shell
    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    aws ecr create-repository --repository-name simple-ne-server --region ${REGION} 
```

7. 进行镜像的标签以及推送

```shell
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    docker tag simple-ne-server:latest_eif ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/simple-ne-server:latest_eif 
    docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/simple-ne-server:latest_eif
```

8. 修改`deploy.yaml` 第25行，将Image 的路径改成上述路径

```yaml
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/simple-ne-server:latest_eif
```

9. 部署Server app 到EKS, 请参考部署输出的EKS command 进行 k8s config更新。

```shell
   # Update ~/.kube/config for interacting with EKS
   # This command can be found in CloudFormation >> Output tab
   # aws eks update-kubeconfig --name cluster-eks_enclaves --region ${REGION} --role-arn arn:aws:iam::${ACCOUNT_ID}:role/EKS-Enclaves-ClusterAdminRole<SUFFIX>
   
   kubectl apply -f deploy.yaml
```

### 构建客户端镜像

11. 进入到Client 的文件夹并构建镜像

```shell
    # was in 101-simple-example/enclavesServer
    cd ../enclavesClient
    docker build -t simple-ne-client:latest .
```

12. 创建 ECR Repository

```shell
    aws ecr create-repository --repository-name simple-ne-client --region ${REGION}
```

13. 打标签推送

```shell
    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    docker tag simple-ne-client:latest ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/simple-ne-client:latest
    docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/simple-ne-client:latest
```

14. 修改`deploy.yaml` 第25行，将Image 的路径改成上述路径

```yaml
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/simple-ne-client:latest
```

15. 部署到EKS

```shell
   # Update ~/.kube/config for interacting with EKS
   # This command can be found in CloudFormation >> Output tab
   #aws eks update-kubeconfig --name cluster-eks_enclaves --region ${REGION} --role-arn arn:aws:iam::$ACCOUNT_ID:role/EKS-Enclaves-ClusterAdminRole<SUFFIX>
   
   kubectl apply -f deploy.yaml
```

----

#### 查看日誌

通过运行以下命令可以查看服务器端的日志和执行结果<br/>

```shell
   kubectl get pods -n fl # you can find a pod name like "server-xxxx-xxxx"
   kubectl logs -f -l app=server -n fl
```

看到如以下结果<br/>

```shell
    Payload JSON is : {"msg":"hello"}
    Message sent back to client
```

通过运行以下命令可以查看客户端的日志和执行结果 <br/>

```shell
   kubectl get pods -n fl # you can find a pod name like "client-xxxx-xxxx"
   kubectl logs -f -l app=client -n fl
```

看到如以下结果<br/>

```shell
   Received msg from Server: {"datetime": "2023/04/02 09:04:43", "json_result": "{\"msg\":\"hello\"}"}
```