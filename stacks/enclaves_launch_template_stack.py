
from aws_cdk import App, Stack, Environment, CfnOutput, RemovalPolicy, Fn
from aws_cdk import (
    aws_ec2 as ec2,
)

from constructs import Construct
import base64

user_data = """MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="==MYBOUNDARY=="

--==MYBOUNDARY==
Content-Type: text/x-shellscript; charset="us-ascii"

#!/bin/bash -e
yum update -y
readonly NE_ALLOCATOR_SPEC_PATH="/etc/nitro_enclaves/allocator.yaml"
# Node resources that will be allocated for Nitro Enclaves
readonly CPU_COUNT=2
readonly MEMORY_MIB=24000

# This step below is needed to install nitro-enclaves-allocator service.
amazon-linux-extras install aws-nitro-enclaves-cli -y

# Update enclave's allocator specification: allocator.yaml
sed -i "s/cpu_count:.*/cpu_count: $CPU_COUNT/g" $NE_ALLOCATOR_SPEC_PATH
sed -i "s/memory_mib:.*/memory_mib: $MEMORY_MIB/g" $NE_ALLOCATOR_SPEC_PATH
# Restart the nitro-enclaves-allocator service to take changes effect.

systemctl restart nitro-enclaves-allocator.service
echo "NE user data script has finished successfully."

--==MYBOUNDARY==--\     #must end with --\
"""

class EnclavesNodeLaunchStack(Stack):
    
    def __init__(self, scope: Construct, id: str, disk_size: int, ebs_iops: int, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.disk_size = disk_size
        self.ebs_iops  = ebs_iops 
        self._create_ec2_launch_template()
    
    def _create_ec2_launch_template(self):
        
        # Create LaunchTemplate
        self.lt = ec2.CfnLaunchTemplate(self, "LaunchTemplate",
            launch_template_name="EKS_Enclaves_NodeGroup_Launch_Template-0",
            launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                instance_type=self.node.try_get_context("enclaves_node_machine_type"),
                user_data=Fn.base64(user_data),
                enclave_options=ec2.CfnLaunchTemplate.EnclaveOptionsProperty(
                    enabled=True
                ), # enable Enclave
                block_device_mappings = [ec2.CfnLaunchTemplate.BlockDeviceMappingProperty(
                        device_name   = "/dev/xvda",
                            ebs       = ec2.CfnLaunchTemplate.EbsProperty(
                            delete_on_termination = True,
                            encrypted             = False, # //TODO - enable for KMS
                            # kms_key_id="kmsKeyId",       # //TODO - enable for KMS
                            iops                  = self.ebs_iops,
                            volume_size           = self.disk_size,
                            volume_type           = "io2"
                        )
                )],
                metadata_options=ec2.CfnLaunchTemplate.MetadataOptionsProperty(
                    http_put_response_hop_limit=1, # block instance metadata access for IRSA 
                    http_tokens="required"
                )
            )
        )
        
        CfnOutput(
                self, "EnclavesNodeLaunchTemplate",
                value=self.lt.ref,
                description="Enclaves Node Launch Template",
                export_name="EnclagesNodeLaunchTemplate"
            )