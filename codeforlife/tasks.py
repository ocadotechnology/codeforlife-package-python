"""
© Ocado Group
Created on 28/03/2025 at 14:37:46(+00:00).

Custom utilities for Celery tasks.
"""

import typing as t
from itertools import islice

from celery import shared_task as _shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.db.models.query import QuerySet, ValuesQuerySet
from google.auth import default, impersonated_credentials
from google.cloud import storage  # type: ignore[import-untyped]


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
        return _shared_task(*args, **kwargs, name=name)(task)

    return wrapper


gcp_project_id = ""
gcs_bucket_name = "BigQueryDataTransfer"
gcs_service_account = ""


def shared_task__save_value_query_set_to_csv_in_gcs_bucket(
    *args,
    folder_name: str,
    chunk_size: int,
    fields: t.List[str],
    time_limit: int = 3600,
    soft_time_limit: int = 3570,
    **kwargs,
):
    """"""

    def wrapper(
        get_query_set: t.Callable[..., QuerySet[t.Any, t.Tuple[t.Any, ...]]]
    ):
        def task(*task_args, **task_kwargs):
            query_set = get_query_set(*task_args, **task_kwargs)
            if query_set.count() == 0:
                return

            # # Get the default credentials from the environment (Workload Identity Federation)
            # # These are the short-lived credentials from the AWS IAM role.
            # creds, _ = default()

            # # Create the impersonated credentials object
            # impersonated_creds = impersonated_credentials.Credentials(
            #     source_credentials=creds,
            #     target_principal=(
            #         gcs_service_account
            #         + f"@{gcp_project_id}.iam.gserviceaccount.com"
            #     ),
            #     # https://cloud.google.com/storage/docs/oauth-scopes
            #     target_scopes=[
            #         "https://www.googleapis.com/auth/devstorage.full_control"
            #     ],
            #     # The lifetime of the impersonated credentials in seconds.
            #     lifetime=time_limit,
            # )

            # # Create a client with the impersonated credentials
            # storage_client = storage.Client(credentials=impersonated_creds)
            # bucket = storage_client.bucket(gcs_bucket_name)

            # TODO: create folder in bucket

            csv = ""
            for i, values in enumerate(
                t.cast(
                    ValuesQuerySet[t.Any, t.Tuple[t.Any, ...]],
                    query_set.values_list(*fields),
                ).iterator(chunk_size=chunk_size)
            ):
                csv = ""
                if i % chunk_size == 0:
                    if i != 0:
                        csv_path = f"{folder_name}/{i - chunk_size}_{i}.csv"
                        # Upload file to bucket

                    csv = ",".join(fields)
                csv += "\n" + ",".join(values)

            # Upload CSV to GCS bucket.

        name = kwargs.pop("name", None)
        name = get_task_name(name if isinstance(name, str) else get_query_set)

        return _shared_task(
            *args,
            **kwargs,
            name=name,
            time_limit=time_limit,
            soft_time_limit=soft_time_limit,
        )(task)

    return wrapper


@shared_task__save_value_query_set_to_csv_in_gcs_bucket(
    folder_name="example", chunk_size=5000
)
def example(bucket: str):
    pass


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
