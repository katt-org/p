#!/usr/bin/env python
""" Organization for katt@defn.sh """

from cdktf import App, TerraformStack
from constructs import Construct
from imports.aws import AwsProvider

from fogg.aws import Organization


class KattStack(TerraformStack):
    """ cdktf Stack for an organization with accounts, sso. """
    def __init__(self, scope: Construct, namespace: str):
        super().__init__(scope, namespace)

        self.Organization()

    def providers(self):
        """ AWS provider in a region with SSO. """
        sso_region = "us-west-2"

        AwsProvider(self, "aws", region=sso_region)

    def organization(self):
        """ Make an Organization with accounts, sso """
        org = "katt"
        domain = "defn.sh"
        accounts = (
            "org",
            "net",
            "log",
            "lib",
            "ops",
            "sec",
            "hub",
            "pub",
            "dev",
            "dmz",
        )

        Organization(self, org, domain, accounts)


app = App()
KattStack(app, "default")

app.synth()
