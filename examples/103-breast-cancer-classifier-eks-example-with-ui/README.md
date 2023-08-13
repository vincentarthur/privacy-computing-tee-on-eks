### Comparing to 103-breast-cancer-classifier-eks-example, 103-breast-cancer-classifier-eks-example-2 has more items as below

- Add features to utilize KMS key to encrypt inference result
- Save encrypted inference result to S3(in tech providers side)
- Add example to decrypt data (run on data owner side)

### [Single AWS Account] Medical Image Diagnosis

- [01. Base Image Creation](/readmes/04_single_aws_account_medical_image_diagnosis/01_build_base_image.md)
- [02. Create KMS Key for Model](/readmes/04_single_aws_account_medical_image_diagnosis/02_create_model_kms.md)
- [03. Build Server App](/readmes/04_single_aws_account_medical_image_diagnosis/03_build_server_app.md)
- [04. Build Client App](/readmes/04_single_aws_account_medical_image_diagnosis/04_build_client_app.md)
- [05. Manual Trigger](/readmes/04_single_aws_account_medical_image_diagnosis/05_manual_trigger.md)

### [Multiple AWS Accounts] Medical Image Diagnosis

- [01. ECR Replication Setup](/readmes/05_multiple_aws_account_medical_image_diagnosis/01_ecr_replication.md)
- [02. Data Owner Setup IRSA](/readmes/05_multiple_aws_account_medical_image_diagnosis/02_data_owner_create_irsa.md)
- [03. Data Owner Creates Data KMS Key](/readmes/05_multiple_aws_account_medical_image_diagnosis/03_data_owner_create_data_kms_key.md)
- [04. Tech Provider Creates Model KMS Key](/readmes/05_multiple_aws_account_medical_image_diagnosis/04_tech_provider_create_model_kms_key.md)
- [05. Tech Provider Builds Server app](/readmes/05_multiple_aws_account_medical_image_diagnosis/05_tech_provider_create_server_app_image.md)
- [06. Data Owner Updates IAM Policy](/readmes/05_multiple_aws_account_medical_image_diagnosis/06_data_owner_update_iam_policy.md)
- [07. Data Owner Builds Env](/readmes/05_multiple_aws_account_medical_image_diagnosis/07_data_owner_build_env.md)
- [08. Data Owner Builds Apps](/readmes/05_multiple_aws_account_medical_image_diagnosis/08_data_owner_build_apps.md)
- [09. Data Owner Triggers Inference](/readmes/05_multiple_aws_account_medical_image_diagnosis/09_data_owner_inference.md)
- [10. Add PCR0 for Cryptographic Attestation](/readmes/05_multiple_aws_account_medical_image_diagnosis/10_add_pcr0_for_cryptographic_attestation.md)

### Notice

```markdown
Difference between `103-breast-cancer-classifier-eks-example-2` and `103-breast-cancer-classifier-eks-example-with-ui`

1. enclaveServer in `103-breast-cancer-classifier-eks-example-2` goes with Image Decryption
2. enclaveServer in `103-breast-cancer-classifier-eks-example-with-ui` goes *WITHOUT* Image Decryption
3. enclaveClient in `103-breast-cancer-classifier-eks-example-with-ui` is a backend application (Flask based)
4. enclaveClientFE in `103-breast-cancer-classifier-eks-example-with-ui` is a frontend application (React based)
```

#### 103-breast-cancer-classifier-eks-example-with-UI Dedicated Notice

1. Need to create folders under S3 bucket (S3 bucket name could be
   like `industry-tee-workshop-${ACCOUNT_ID}-${REGION}-kms-bucket`)

```yaml
- s3_bucket
  - source       # use to store source images
  - thumbnails   # use to store thumbnails images. File name should look like "xxxx.png.thumbnail"
```

2. In `enclaveClient/deploy.yaml`, please input S3 location. This S3 bucket stores source and thumbnail images for
   display and prediction.<br/>

```yaml
 - name: IMAGES_S3_BUCKET_LOCATION
   value: "<NEED INPUT>/source"
```

3. In `enclaveClientFE/deploy.yaml`, please input Application LoadBalancer URL. This URL will be display when INGRESS
   deployed.

```yaml
# line 41
env:
  - name: REACT_APP_ALB_URL
    value: "<Need to update>"
```

---

### Build and Deployment Flow

#### EnclaveServer

```shell
cd 103-breast-cancer-classifier-eks-example-with-ui/enclaveServer
bash build_script.sh
```

#### EnclaveClient

```shell
cd 103-breast-cancer-classifier-eks-example-with-ui/enclaveClient
bash build.sh

kubectl apply -f deploy.yaml
kubectl apply -f client-svc.yaml
```

#### EnclaveClientFE

```shell
cd 103-breast-cancer-classifier-eks-example-with-ui/enclaveClientFE
bash build.sh
## Ensure you update kubeconfig with executing 
## aws eks update-kubeconfig --name cluster-eks-enclaves --region ${REGION} --role-arn arn:aws:iam::${ACCOUNT_ID}:role/EKS-Enclaves-ClusterAdminRole<SUFFIX>
kubectl apply -f deploy.yaml

kubectl apply -f ui-svc.yaml

kubectl apply -f ingress.yaml

# After triggered ingress deployment, wait 3-4 mins and check the domain name of INGRESS, with executing
# somthing like : k8s-fl-clientui-xxxxxx-xxxxxx.us-east-1.elb.amazonaws.com
kubectl get ingress -n fl
```

On Cloud9, click and open `enclaveClientFE/deploy.yaml`, input `ALB domain` into `line 43`:

```yaml
 env:
   - name: REACT_APP_ALB_URL
     value: "<Need to update>"
```

Update deployment to take effective in frontend deployment.

```shell
kubectl apply -f deploy.yaml
```

### Access UI

Open browser and paste ALB domain to access<br /><br />
![industryscenario-2-ui-overview.png](/static/industryscenario-2-ui-overview.png)<br /><br />

Select "image" for prediction, and click `Predict`, wait 10-20s, get the result.<br /><br />
![industryscenario-2-ui-result.png](/static/industryscenario-2-ui-result.png)<br /><br />