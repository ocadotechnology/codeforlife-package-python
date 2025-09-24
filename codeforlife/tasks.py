"""
© Ocado Group
Created on 28/03/2025 at 14:37:46(+00:00).

Custom utilities for Celery tasks.
"""

import typing as t

from celery import Task
from celery import shared_task as _shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from google.auth import default, impersonated_credentials
from google.cloud import storage


def get_task_name(task: t.Union[str, t.Callable]):
    """Namespace a task by the service it's in.

    Args:
        task: The name of the task.

    Returns:
        The name of the task in the format: "{SERVICE_NAME}.{TASK_NAME}".
    """

    if callable(task):
        task = f"{task.__module__}.{task.__name__}"

    return f"{settings.SERVICE_NAME}.{task}"


def shared_task(*args, **kwargs):
    """
    Wrapper around Celery's default shared_task decorator which namespaces all
    tasks to a specific service.
    """

    if len(args) == 1 and callable(args[0]):
        task = args[0]
        return _shared_task(name=get_task_name(task))(task)

    def wrapper(task: t.Callable):
        name = kwargs.pop("name", None)
        name = get_task_name(name if isinstance(name, str) else task)
        return _shared_task(name=name, *args, **kwargs)(task)

    return wrapper


def shared_gcs_task(task: t.Callable[[storage.Bucket], None]):
    """Shared GCS task.

    Args:
        task: _description_

    Raises:
        ex: _description_
    """
    gcs_bucket_name = "BigQueryDataTransfer"
    gcp_project_id = ""
    gcs_service_account = ""

    time_limit = 3600
    soft_time_limit = 3570

    def wrapper(*args, **kwargs):
        # Get the default credentials from the environment (Workload Identity Federation)
        # These are the short-lived credentials from the AWS IAM role.
        creds, _ = default()

        # Create the impersonated credentials object
        impersonated_creds = impersonated_credentials.Credentials(
            source_credentials=creds,
            target_principal=(
                gcs_service_account
                + f"@{gcp_project_id}.iam.gserviceaccount.com"
            ),
            # https://cloud.google.com/storage/docs/oauth-scopes
            target_scopes=[
                "https://www.googleapis.com/auth/devstorage.full_control"
            ],
            # The lifetime of the impersonated credentials in seconds.
            lifetime=time_limit,
        )

        # Create a client with the impersonated credentials
        storage_client = storage.Client(credentials=impersonated_creds)
        bucket = storage_client.bucket(gcs_bucket_name)

        try:
            task(bucket, *args, **kwargs)
        except SoftTimeLimitExceeded as ex:
            raise ex

    _shared_task(
        name=get_task_name(task),
        soft_time_limit=soft_time_limit,
        time_limit=time_limit,
    )(wrapper)


def get_local_sqs_url(aws_region: str, service_name: str):
    """Get the URL of an SQS queue in the local environment.

    Args:
        aws_region: The AWS region.
        service_name: The service this SQS queue belongs to.

    Returns:
        The SQS queue's URL.
    """
    return (
        f"http://sqs.{aws_region}.localhost.localstack.cloud:4566"
        f"/000000000000/{service_name}"
    )
