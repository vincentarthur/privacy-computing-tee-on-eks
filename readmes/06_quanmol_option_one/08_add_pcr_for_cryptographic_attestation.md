---
title: "步骤 8: 追加PCR实现加密验证"
weight: 10
---

> 预计花费时间：30分钟
> 目前的REGION 请选择 US-EAST-1

⚠️ *注意事项*

1. PCR值是在构建Enclave Image File (.eif)时候输出的，需要注意保存
2. PCR值是Nitro Enclave基于EIF、应用以及内核计算出来的Hash值，用于实现`Cryptographic Attestation`(安全验证)
3. 要实现`Cryptographic Attestation`(PCR)需要禁止nitro-cli console的运行 (禁止以debug模式运行)。因为一旦开启console以及debug模式，Nitro
   Hypervisor就不会使用真实的PCR0进行验证，而使用`000000000000000000000000000000000000000000000000`作为attestation
   document生成的依据。因此需要在生产环境中注意。

### 基于上述注意事项，需要进行以下操作:

`QuanMol`需要完成：

1. 修改`run.sh`, 去掉`nitro-cli console`步骤
2. 重新构建Docker Image, 并推送到ECR

---

### 修改run.sh, disable nitro-cli console

1. 在Cloud9中打开`enclaveServer/run.sh`

```shell
    # 注释 14-19行
#    local enclave_id=$(nitro-cli describe-enclaves | jq -r ".[0].EnclaveID")
#    echo "-------------------------------"
#    echo "Enclave ID is $enclave_id"
#    echo "-------------------------------"
#   
#    nitro-cli console --enclave-id "${enclave_id}" # blocking call.
```

2. 重新构建image 以及推送

```shell
    docker build -t breast-cancer-classifier:latest .
    sudo nitro-cli build-enclave --docker-uri breast-cancer-classifier:latest --output-file breast-cancer-classifier.eif
    docker build -t breast-cancer-classifier:latest_eif -f Dockerfile.eif .

```

⚠️ 注意：请保存 __PCR0的值__ 再往下操作。

```shell
    ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    REGION=$(curl http://169.254.169.254/latest/meta-data/placement/region -s)
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com
    docker tag breast-cancer-classifier:latest_eif ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier:latest_eif
    docker push ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/breast-cancer-classifier:latest_eif
```

### 数据拥有方的修改

以下操作需要数据拥有方进行操作：

- 修改`DataKeyForEnclaves` KMS Policy,追加关于`PCR`的条件 <br /><br />
- 联合测试


1. 在Cloud9 命令行中运行<br /><br />

```shell
    # DATA_KEY_ID 需要在 AWS Console KMS dashboard 获取 
    aws kms get-key-policy --key-id ${DATA_KEY_ID} --policy-name default --output text > DATA_KEY_ID_key_policy.json
```

2. 在第27行(`"Resource": "*"`后) 追加以下內容。（可根据需求添加更多PCR值）<br /><br />

```text
    ,
    "Condition": {
        "StringEqualsIgnoreCase": {
        "kms:RecipientAttestation:PCR0": "<PCR0 from eif output>"
        }
    }
```

5. 在Cloud9命令行中运行以下命令更新KMS策略。<br /><br />

```shell
    aws kms put-key-policy --policy-name default --key-id ${MODEL_KEY_ID} --policy file://MODEL_KEY_ID_key_policy.json
```

---

### 重新部署服务端应用

```shell
#    cd ../enclaveServer
    kubectl apply -f deploy.yaml
```

![industryscenario-2-multi-account-pcr-verification-server-output.png](/static/industryscenario-2-multi-account-pcr-verification-server-output.png) <br /><br />

### 参照Step 7 发起推理请求

```text
得到以下结果
```

![industryscenario-2-multi-account-pcr-verification-output.png](/static/industryscenario-2-multi-account-pcr-verification-output.png)

---

### 如何验证是否PCR0 限制了KMS Key访问？

可以在`QuanMol`方进行验证, 通过直接在Client Pod中模拟`仅使用IRSA`访问KMS，预期结果是`AccessDenied`。 <br />

1. 在Cloud9中 通过`kubectl exec `命令进入 __客户端程序__ 。创建新的测试代码文件 <br /><br />

```shell
    touch spike_test.py
```

2. 复制以下代码，粘贴到`spike_test.py`中，并将`DataKeyForEnclaves` 的KMS ARN ID填入`key_id` <br /><br />

```python
import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()


class KeyManager:
    def __init__(self, kms_client):
        self.kms_client = kms_client
        self.created_keys = []

    def generate_data_key(self, key_id):
        """
        Generates a symmetric data key that can be used for client-side encryption.
        """

        try:
            data_key = self.kms_client.generate_data_key(KeyId=key_id, KeySpec='AES_256')
        except ClientError as err:
            logger.error(
                "Couldn't generate a data key for key %s. Here's why: %s",
                key_id, err.response['Error'])
        else:
            print(data_key)


if __name__ == '__main__':
    kms_client = boto3.client('kms')
    key_id = ''

    km = KeyManager(kms_client)
    km.generate_data_key(key_id)

```

3. 运行代码。该代码向`DataKeyForEnclaves`申请生成data key。<br /><br />

```shell
   python3 spike_test.py
```

4. 得到如下结果: <br /><br />
   ![industryscenario-2-multi-account-pcr-verification-output-accessdenied.png](/static/industryscenario-2-multi-account-pcr-verification-output-accessdenied.png)

得到的错误为`Access Denied`,其原因为当前的KMS Key policy 添加了对于`PCR0`的条件，即需要同时满足IAM 以及PCR0 才能获得授权。<br />
因此此方法可以 __有效防止__ `QuanMol`试图仅通过IAM获得密钥对数据进行解密, 达到保护数据的目的。