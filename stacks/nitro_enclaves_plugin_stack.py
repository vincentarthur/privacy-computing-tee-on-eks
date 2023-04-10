#!/usr/bin/env python3

from aws_cdk import App, Stack, Environment, CfnOutput, RemovalPolicy, Fn, CfnResource
from aws_cdk import (
    aws_ec2 as ec2,
)

from constructs import Construct

"""
    This stack uses to install nitro enclaves device plugin to EKS cluster.
    With
    1. Create Daemonset
    2. label specific node with labels
"""

class DevicePluginInstallationStack(Stack):
    
    def __init__(self, scope: Construct, id: str, eks_cluster: CfnResource, daemonset_manifest:str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self._install_device_plugin(eks_cluster, daemonset_manifest)
        
    def _install_device_plugin(self, eks_cluster: CfnResource, daemonset_manifest):
        eks_cluster.add_manifest( 'device_plugin',
            daemonset_manifest
        )