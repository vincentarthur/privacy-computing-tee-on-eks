import os.path

from aws_cdk.aws_s3_assets import Asset
from aws_cdk.aws_autoscaling import AutoScalingGroup, BlockDevice, BlockDeviceVolume

from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    App, Stack,
    aws_elasticloadbalancingv2 as elbv2,
    Fn
)

from constructs import Construct

dirname = os.path.dirname(__file__)

# Read content from script
user_data_script_content = ""
with open(f"{dirname}/manifest/arbiter_server_user_data.sh") as f:
    user_data_script_content = f.read()

class FlArbiterServerStack(Stack):

    def __init__(self, scope: Construct, id: str, disk_size: int, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "VPC",
            nat_gateways=0,
            subnet_configuration=[ec2.SubnetConfiguration(name="public",subnet_type=ec2.SubnetType.PUBLIC)]
            )

        # AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation     = ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition        = ec2.AmazonLinuxEdition.STANDARD,
            virtualization = ec2.AmazonLinuxVirt.HVM,
            storage        = ec2.AmazonLinuxStorage.GENERAL_PURPOSE
            )

        # Instance Role and SSM Managed Policy
        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))

        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
            
        security_group = ec2.SecurityGroup(self, "SecurityGroup", vpc=vpc)
        
        
        # Configure UserData
        # commands_user_data = ec2.UserData.for_linux()
        # commands_user_data.add_execute_file_command(file_path = './manifest/arbiter_server_user_data.sh')
        
        
        # Configure ASG
        asg = AutoScalingGroup(self, "ASG",
            vpc            = vpc,
            instance_type  = ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.LARGE),
            machine_image  = ec2.AmazonLinuxImage(),
            security_group = security_group,
            role           = role,
            block_devices  = [
                BlockDevice(
                    device_name = "/dev/xvda",
                    volume      = BlockDeviceVolume.ebs(disk_size),
                )
            ],
            user_data      = ec2.UserData.custom(user_data_script_content) #Fn.base64(user_data_script_content),
        )
        
        # asg: AutoScalingGroup
        # Create the load balancer in a VPC. 'internetFacing' is 'false'
        # by default, which creates an internal load balancer.
        lb = elbv2.ApplicationLoadBalancer(self, "LB",
            vpc             = vpc,
            internet_facing = True
        )
        
        # Add a listener and open up the load balancer's security group
        # to the world.
        listener = lb.add_listener("Listener",
            port=80,
        
            # 'open: true' is the default, you can leave it out if you want. Set it
            # to 'false' and use `listener.connections` if you want to be selective
            # about who can access the load balancer.
            open=True
        )
        
        # Create an AutoScaling group and add it as a load balancing
        # target to the listener.
        listener.add_targets("ApplicationFleet",
            port    = 8080,
            targets = [asg]
        )