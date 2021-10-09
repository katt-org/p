#!/usr/bin/env python
""" Creates Organizations, Accounts, and Administrator permission set """

from cdktf import Fn
from imports.aws import (
    DataAwsIdentitystoreGroup,
    DataAwsSsoadminInstances,
    OrganizationsAccount,
    OrganizationsOrganization,
    SsoadminAccountAssignment,
    SsoadminManagedPolicyAttachment,
    SsoadminPermissionSet,
)


def administrator(self, ssoadmin_instances):
    """ Administrator SSO permission set with AdministratorAccess policy"""
    resource = SsoadminPermissionSet(
        self,
        "admin_sso_permission_set",
        name="Administrator",
        instance_arn=Fn.element(Fn.tolist(ssoadmin_instances.arns), 0),
        session_duration="PT2H",
        tags={"ManagedBy": "Terraform"},
    )

    SsoadminManagedPolicyAttachment(
        self,
        "admin_sso_managed_policy_attachment",
        instance_arn=resource.instance_arn,
        permission_set_arn=resource.arn,
        managed_policy_arn="arn:aws:iam::aws:policy/AdministratorAccess",
    )

    return resource


def account(self, org, domain, acct, identitystore_group,
            sso_permission_set_admin):
    """ Create the organization account. """
    match acct:
        case "org":
            # The master organization account can't set
            # iam_user_access_to_billing, role_name
            organizations_account = OrganizationsAccount(
                self,
                acct,
                name=acct,
                email=f"{org}+{acct}@{domain}",
                tags={"ManagedBy": "Terraform"},
            )
        case _:
            # Organization account
            organizations_account = OrganizationsAccount(
                self,
                acct,
                name=acct,
                email=f"{org}+{acct}@{domain}",
                iam_user_access_to_billing="ALLOW",
                role_name="OrganizationAccountAccessRole",
                tags={"ManagedBy": "Terraform"},
            )

    # Organization accounts grant Administrator permission set to the Administrator group
    SsoadminAccountAssignment(
        self,
        f"{acct}_admin_sso_account_assignment",
        instance_arn=sso_permission_set_admin.instance_arn,
        permission_set_arn=sso_permission_set_admin.arn,
        principal_id=identitystore_group.group_id,
        principal_type="GROUP",
        target_id=organizations_account.id,
        target_type="AWS_ACCOUNT",
    )


def organization(self, org, domain, accounts):
    """ The organization must be imported. """
    OrganizationsOrganization(
        self,
        "organization",
        feature_set="ALL",
        enabled_policy_types=["SERVICE_CONTROL_POLICY", "TAG_POLICY"],
        aws_service_access_principals=[
            "cloudtrail.amazonaws.com",
            "config.amazonaws.com",
            "ram.amazonaws.com",
            "ssm.amazonaws.com",
            "sso.amazonaws.com",
            "tagpolicies.tag.amazonaws.com",
        ],
    )

    # Lookup pre-enabled AWS SSO instance
    ssoadmin_instances = DataAwsSsoadminInstances(self, "sso_instance")

    # Administrator SSO permission set with AdministratorAccess policy
    sso_permission_set_admin = administrator(self, ssoadmin_instances)

    # Lookup pre-created Administrators group
    identitystore_group = DataAwsIdentitystoreGroup(
        self,
        "administrators_sso_group",
        identity_store_id=Fn.element(
            Fn.tolist(ssoadmin_instances.identity_store_ids), 0
        ),
        filter=[
            {"attributePath": "DisplayName", "attributeValue": "Administrators"}
        ],
    )

    # The master account (named "org") must be imported.
    for acct in accounts:
        account(self, org, domain, acct, identitystore_group,
                sso_permission_set_admin)