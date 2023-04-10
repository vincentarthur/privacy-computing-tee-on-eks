In this sample, we'd will create a simple C/S workload and run on Nitro Enclaves (EKS).

For Server Side, we will create a simple server to listen "Any of CID". It will accept requests from clients, and response message with adding Datetime.

Build "enclave_base" image
```
  docker build ./ -t "enclave_base"
```


Steps to build Server Side assets:

1. Build docker image

```
    cd 101-simple-example/enclavesServer
    docker build -t simple-ne-server:latest .
```

2. Create Enclaves Image File (EIF) for server image
```
   nitro-cli build-enclave --docker-uri simple-ne-server:latest --output-file simple-ne-server.eif 
```

3. Create Docker file for wrapping EIF file, this image will be pushed to ECR for EKS execution
```
   docker build -t simple-ne-server:latest_eif -f Dockerfile.eif
```

4. Create ECR repository for storing server EIF. Change REGION accordingly.
```
    aws ecr create-repository --repository-name simple-ne-server --region us-east-1 
```

5. Tag docker image and push. Please correct the ACCOUNT_ID and REGION
```
    aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
    docker tag simple-ne-server:latest_eif <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/simple-ne-server:latest_eif 
    docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/simple-ne-server:latest_eif
```

6. Change the YAML file for running Server-app on EKS
```
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/simple-ne-server:latest_eif
```

7. Deploy Server-app to EKS
```
   # Update ~/.kube/config for interacting with EKS
   # This command can be found in CloudFormation >> Output tab
   aws eks update-kubeconfig --name cluster-eks_enclaves --region <REGION> --role-arn arn:aws:iam::<ACCOUNT_ID>:role/EKS-Enclaves-ClusterAdminRole<SUFFIX>
   
   kubectl apply -f deploy.yaml
```

8. Check the log
```
   kubectl get pods -n fl # you can find a pod name like "server-xxxx-xxxx"
   kubectl logs -f -l app=server -n fl
```

Steps to build Client Side assets:
1. Build docker image

```
    cd 101-simple-example/enclavesClient
    docker build -t simple-ne-client:latest .
```

2. Create ECR repository for storing server EIF. Change REGION accordingly.
```
    aws ecr create-repository --repository-name simple-ne-client --region us-east-1 
```

5. Tag docker image and push. Please correct the ACCOUNT_ID and REGION
```
    aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com
    docker tag simple-ne-client:latest <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/simple-ne-client:latest
    docker push <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/simple-ne-client:latest
```

6. Change the YAML file for running Client-app on EKS
```
    #Change line 25 to point to your own IMAGE uri.
    - image: <ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/simple-ne-client:latest
```

7. Deploy Clien-app to EKS
```
   # Update ~/.kube/config for interacting with EKS
   # This command can be found in CloudFormation >> Output tab
   aws eks update-kubeconfig --name cluster-eks_enclaves --region <REGION> --role-arn arn:aws:iam::<ACCOUNT_ID>:role/EKS-Enclaves-ClusterAdminRole<SUFFIX>
   
   kubectl apply -f deploy.yaml
```

8. Check the log
```
   kubectl get pods -n fl # you can find a pod name like "client-xxxx-xxxx"
   kubectl logs -f -l app=client -n fl
```


### Finally you should see something from Client & Server console, as below:
Server: 
```
    Payload JSON is : {"msg":"hello"}
    Message sent back to client
```

Client: 
```
   Received msg from Server: {"datetime": "2023/04/02 09:04:43", "json_result": "{\"msg\":\"hello\"}"}
```