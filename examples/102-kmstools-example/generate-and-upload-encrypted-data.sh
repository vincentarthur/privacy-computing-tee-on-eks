#!/bin/bash

############################################################################
#
# The example of generating a encrypted file and push to S3 for decrypting
# testing.
#
# Before executing the script, please ensure the IAM role has permission to
# call Encrypt/Decrypt for specific KMS key.
#
############################################################################

usage(){
    echo "Expect parameters: S3_BUCKET_NAME, KMS_KEY_ID(arn) and REGION"
    echo "bash $0 <bucket_name> <key_arn_id> <region>"
    echo "Example: bash $0 privacy-computing-assets-us-east-1 arn:aws:kms:us-east-1:xxx:key/b4c01ff4-8a9f-4ee3-b3fc-87bf852c0369 us-east-1"
}

if [[ $# -eq 0 || $# -lt 3 ]];then
  echo "Missing required parameters."
  usage
  exit 999
fi

TARGET_S3_BUCKET=$1
TARGET_S3_URI="s3://$1"
KMS_ARN_ID=$2
REGION=$3

export AWS_REGION=$REGION
rm -f encrypted_data.txt
echo -n $(aws kms encrypt --key-id "${KMS_ARN_ID}" --region ${REGION} --cli-binary-format raw-in-base64-out --plaintext "example-encrypted-text" | jq -r ".CiphertextBlob") >  encrypted_data.txt
aws s3 cp encrypted_data.txt $TARGET_S3_URI
