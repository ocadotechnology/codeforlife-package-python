"""
© Ocado Group
Created on 04/12/2025 at 18:58:44(+00:00).

Authentication credentials.
"""

import typing as t

from boto3 import Session as AwsSession
from django.conf import settings
from google.auth.aws import (
    AwsSecurityCredentials,
    AwsSecurityCredentialsSupplier,
)
from google.auth.aws import Credentials as AwsCredentials
from google.auth.credentials import Credentials
from google.oauth2.service_account import (
    Credentials as GcpServiceAccountCredentials,
)


class AwsSessionSecurityCredentialsSupplier(AwsSecurityCredentialsSupplier):
    """Supplies AWS security credentials from the current boto3 session."""

    def get_aws_region(self, _, __):
        return settings.AWS_REGION

    def get_aws_security_credentials(self, _, __) -> AwsSecurityCredentials:
        aws_credentials = AwsSession().get_credentials()
        assert aws_credentials

        aws_read_only_credentials = aws_credentials.get_frozen_credentials()
        assert aws_read_only_credentials.access_key
        assert aws_read_only_credentials.secret_key
        assert aws_read_only_credentials.token

        return AwsSecurityCredentials(
            access_key_id=aws_read_only_credentials.access_key,
            secret_access_key=aws_read_only_credentials.secret_key,
            session_token=aws_read_only_credentials.token,
        )


# pylint: disable-next=abstract-method,too-many-ancestors
class GcpWifCredentials(AwsCredentials):
    """Workload Identity Federation credentials for GCP using AWS IAM roles."""

    def __init__(self, token_lifetime_seconds: int = 600):
        super().__init__(
            subject_token_type="urn:ietf:params:aws:token-type:aws4_request",
            audience=settings.GCP_WIF_AUDIENCE,
            universe_domain="googleapis.com",
            token_url="https://sts.googleapis.com/v1/token",
            service_account_impersonation_url=(
                "https://iamcredentials.googleapis.com/v1/projects/-/"
                f"serviceAccounts/{settings.GCP_WIF_SERVICE_ACCOUNT}"
                ":generateAccessToken"
            ),
            service_account_impersonation_options={
                "token_lifetime_seconds": token_lifetime_seconds
            },
            aws_security_credentials_supplier=(
                AwsSessionSecurityCredentialsSupplier()
            ),
        )


def get_gcp_service_account_credentials(
    token_lifetime_seconds: int = 600,
    service_account_json: t.Optional[str] = None,
) -> Credentials:
    """Get GCP service account credentials.

    Args:
        token_lifetime_seconds: The lifetime of the token in seconds.
        service_account_json: The path to the service account JSON file.

    Returns:
        The GCP service account credentials.
    """
    if settings.ENV != "local":
        return GcpWifCredentials(token_lifetime_seconds=token_lifetime_seconds)
    assert (
        service_account_json
    ), "Service account JSON file path must be provided in local environment."

    return GcpServiceAccountCredentials.from_service_account_file(
        service_account_json
    )
