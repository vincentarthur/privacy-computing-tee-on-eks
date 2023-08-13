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

#### 103-breast-cancer-classifier-eks-example-2 Dedicated Notice

1. on `enclaveClient/deployment.yaml`, please also input S3 location. This S3 bucket will store encrypted result.<br/>
   Ongoing this S3 bucket can setup replication to customer's S3 bucket for synchronizing result to remote.

```yaml
    - name: RESULT_UPLOAD_BUCKET
      value: "NEED INPUT"
```

2. The KMS key used to encrypt inference result in `Server Side`, is exactly same KMS key to decrypt the data. <br/>
   So no leakage risk, due to PCR0 condition has been added to KMS Key policy to restrict access from EIF and IRSA. Only
   IRSA does not work.

---

#### 103-breast-cancer-classifier-eks-example-3 Dedicated Notice
# need to create S3 bucket for storing images with below folder
#   |- source 
#   |- thumbnails (image name : xxxx.png.thumbnail)
# need to add S3 access to IRSA iam role
1. on `enclaveClient/deployment.yaml`, please also input S3 location. This S3 bucket will store encrypted result.<br/>
   Ongoing this S3 bucket can setup replication to customer's S3 bucket for synchronizing result to remote.

```yaml
    - name: RESULT_UPLOAD_BUCKET
      value: "NEED INPUT"
```

2. The KMS key used to encrypt inference result in `Server Side`, is exactly same KMS key to decrypt the data. <br/>
   So no leakage risk, due to PCR0 condition has been added to KMS Key policy to restrict access from EIF and IRSA. Only
   IRSA does not work.

---

### Data Owner how to decrypt data ?

⚠️ Please run below sections in an environment with sufficient permission (like EC2/Cloud9 with S3 bucket & KMS access)

1. Under `utils` folder, there is a `end_user_decrypt_data_sample.py`. User needs to change line 69 & 70:

```python
bucket_name = "<S3_Bucket_with_Replication_from_TechProvider>"
object_name = "<Encrypted result file name (with prefix)>"
```

2. Install required dependencies

```shell
pip install -r requirements.txt
```

3. Run below command to decrypt result

```shell
python3 end_user_decrypt_data_sample.py
```

---

