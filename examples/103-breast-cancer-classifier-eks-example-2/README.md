### Comparing to 103-breast-cancer-classifier-eks-example, 103-breast-cancer-classifier-eks-example-2 has more items as below

- Add features to utilize KMS key to encrypt inference result
- Save encrypted inference result to S3(in tech providers side)
- Add example to decrypt data (run on data owner side)

### [Multiple AWS Accounts] QuanMol Dedicated

- [01. QuanMol IRSA Setup](/readmes/06_quanmol_option_one/01_quanmol_create_irsa_role.md)
- [02. Setup S3](/readmes/06_quanmol_option_one/02_setup_s3.md)
- [03. QuanMol Create Docker Image](/readmes/06_quanmol_option_one/03_quanmol_create_docker_image.md)
- [04. Data Owner Create Data KMS Key](/readmes/06_quanmol_option_one/04_data_owner_create_data_kms_key.md)
- [05. QuanMol Build Env](/readmes/06_quanmol_option_one/05_quanmol_build_env.md)
- [06. Data Owner Prepare Data](/readmes/06_quanmol_option_one/06_data_owner_prepare_data.md)
- [07. Tradeoff - QuanMol Inference](/readmes/06_quanmol_option_one/07_tradeoff_quanmol_inference.md)
- [08. Add PCR0 for Cryptographic Attestation](/readmes/06_quanmol_option_one/08_add_pcr_for_cryptographic_attestation.md)
- [09. Data Owner Decrypt Result](/readmes/06_quanmol_option_one/09_data_owner_decrypt_result.md)

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

