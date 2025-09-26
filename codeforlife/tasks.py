"""
© Ocado Group
Created on 28/03/2025 at 14:37:46(+00:00).

Custom utilities for Celery tasks.
"""

import logging
import typing as t

from celery import shared_task as _shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.db.models.query import QuerySet, ValuesQuerySet
from google.auth import default, impersonated_credentials
from google.cloud import storage  # type: ignore[import-untyped]

_BQ_TABLE_NAMES: t.Set[str] = set()


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


def save_query_set_to_csv_in_gcs_bucket(
    *args,
    bq_table_name: str,
    bq_table_write_mode: t.Literal["overwrite", "append"],
    chunk_size: int,
    fields: t.List[str],
    time_limit: int = 3600,
    soft_time_limit: int = 3570,
    **kwargs,
):
    # pylint: disable=line-too-long
    """Create a Celery task that saves a queryset as CSV files in the GCS bucket.

    Ultimately, these CSV files are imported into a BigQuery table and deleted
    from the GCS bucket. Each task should be given a distinct table name and
    queryset.

    Args:
        bq_table_name: The name of the BigQuery table where these CSV will ultimately be imported into.
        bq_table_write_mode: How the new values are written to the BigQuery table.
        chunk_size: The number of value-rows per CSV.
        fields: The model-fields to include in the CSV.
        time_limit: The maximum amount of time this task is allowed to take before it's hard-killed.
        soft_time_limit: The maximum amount of time this task is allowed to take before it's soft-killed.

    Returns:
        A wrapper function which expects to receive a callback that returns a
        queryset and creates a Celery task to save the queryset as CSV files in
        the GCS bucket.
    """
    # pylint: enable=line-too-long

    if not bq_table_name:
        raise ValueError("A blank BigQuery table names is not allowed.")
    if bq_table_name in _BQ_TABLE_NAMES:
        raise ValueError(
            f'The BigQuery table name "{bq_table_name}" is already registered.'
        )
    if chunk_size <= 0:
        raise ValueError("The chunk size must be greater than 0.")
    if not fields:
        raise ValueError("Must provide at least 1 or more model fields.")
    if time_limit <= 0:
        raise ValueError("The time limit must be greater than 0.")
    if soft_time_limit > time_limit:
        raise ValueError("The soft time limit must be less than or equal to 0.")
    if soft_time_limit <= 0:
        raise ValueError("The soft time limit must be greater than 0.")

    _BQ_TABLE_NAMES.add(bq_table_name)
    chunk_size_digits = len(str(chunk_size))

    def wrapper(
        get_query_set: t.Callable[..., QuerySet[t.Any, t.Tuple[t.Any, ...]]]
    ):
        def task(*task_args, **task_kwargs):
            query_set = get_query_set(*task_args, **task_kwargs)
            if query_set.count() == 0:
                return

            # Get the default credentials from the environment (Workload Identity Federation)
            # These are the short-lived credentials from the AWS IAM role.
            # creds, _ = default()

            # Create the impersonated credentials object
            impersonated_creds = impersonated_credentials.Credentials(
                # source_credentials=creds,
                target_principal=(
                    settings.GOOGLE_CLOUD_STORAGE_SERVICE_ACCOUNT_NAME
                ),
                # https://cloud.google.com/storage/docs/oauth-scopes
                target_scopes=[
                    "https://www.googleapis.com/auth/devstorage.full_control"
                ],
                # The lifetime of the impersonated credentials in seconds.
                lifetime=time_limit,
            )

            # Create a client with the impersonated credentials.
            storage_client = storage.Client(credentials=impersonated_creds)
            bucket = storage_client.bucket(
                settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME
            )

            # bucket.list_blobs(prefix=f"{bq_table_name}/")

            # Track the current value-index and CSV.
            value_index, csv = 0, ""

            def upload_csv():
                chunk_end = str(value_index)
                if value_index == chunk_size:
                    chunk_start = "1".zfill(chunk_size_digits)
                elif value_index < chunk_size:
                    chunk_start = "1".zfill(chunk_size_digits)
                    chunk_end = chunk_end.zfill(chunk_size_digits)
                else:  # value_index > chunk_size
                    chunk_start = str(value_index - chunk_size)

                csv_path = f"{bq_table_name}/{chunk_start}_{chunk_end}.csv"
                logging.info(f"Uploading {csv_path} to bucket.")

                # Create a blob object for the destination path.
                blob = bucket.blob(csv_path)
                blob.upload_from_string(csv, content_type="text/csv")

            for value_index, values in enumerate(
                t.cast(
                    ValuesQuerySet[t.Any, t.Tuple[t.Any, ...]],
                    query_set.values_list(*fields),
                ).iterator(chunk_size=chunk_size)
            ):
                if value_index % chunk_size == 0:
                    if value_index != 0:
                        upload_csv()

                    csv = ",".join(fields)
                csv += "\n" + ",".join(values)

            if value_index != 0 and value_index % chunk_size != 0:
                upload_csv()

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
