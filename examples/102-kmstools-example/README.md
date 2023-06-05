In this sample, we'd will create a simple C/S workload and run on Nitro Enclaves (EKS).

For Server Side, we will create a simple server to listen "Any of CID". It will wait and accept requests from Client.
Client side will pass data s3 uri and KMS key to server. Server will retrieve KMS key to decrypt data in Nitro Enclaves,
implementating fully secure processing.

** The KMS key is from other ACCOUNT, acting as TECH_Provider decryption key.

- [02. KMS Integration](/readmes/03_simple_examples/02_kms_integration.md)