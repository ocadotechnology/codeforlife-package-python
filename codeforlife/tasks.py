"""
© Ocado Group
Created on 28/03/2025 at 14:37:46(+00:00).

Custom utilities for Celery tasks.
"""

import logging
import re
import typing as t
from datetime import datetime

from celery import shared_task as _shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.db.models.query import QuerySet
from django.utils import timezone
from google.auth import impersonated_credentials  # default
from google.cloud import storage as gcs  # type: ignore[import-untyped]

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


# pylint: disable-next=too-many-arguments,too-many-statements
def save_query_set_to_csv_in_gcs_bucket(
    *args,
    bq_table_write_mode: t.Literal["overwrite", "append"],
    chunk_size: int,
    fields: t.List[str],
    time_limit: int = 3600,
    soft_time_limit: int = 3570,
    bq_table_name: t.Optional[str] = None,
    **kwargs,
):
    # pylint: disable=line-too-long
    """Create a Celery task that saves a queryset as CSV files in the GCS bucket.

    Ultimately, these CSV files are imported into a BigQuery table and deleted
    from the GCS bucket. Each task should be given a distinct table name and
    queryset.

    Example:
        ```
        @save_query_set_to_csv_in_gcs_bucket(
            bq_table_write_mode="append",
            chunk_size=1000,
            fields=["first_name", "joined_at", "is_active"],
        )
        def user(): # CSVs will be saved to a BQ table named "user"
            return User.objects.all()
        ```

    Args:
        bq_table_write_mode: How the new values are written to the BigQuery table.
        chunk_size: The number of value-rows per CSV. Must be a multiple of 10.
        fields: The model-fields to include in the CSV.
        time_limit: The maximum amount of time this task is allowed to take before it's hard-killed.
        soft_time_limit: The maximum amount of time this task is allowed to take before it's soft-killed.
        bq_table_name: The name of the BigQuery table where these CSV will ultimately be imported into. If not provided, the name of the decorated function will be used instead.

    Returns:
        A wrapper function which expects to receive a callback that returns a
        queryset and creates a Celery task to save the queryset as CSV files in
        the GCS bucket.
    """
    # pylint: enable=line-too-long

    # Ensure the ID field is always present.
    if "id" not in fields:
        fields.append("id")

    # Validate args.
    if chunk_size <= 0:
        raise ValueError("The chunk size must be > 0.")
    if chunk_size % 10 != 0:
        raise ValueError("The chunk size must be a multiple of 10.")
    if len(fields) <= 1:
        raise ValueError('Must provide at least 1 field (not including "id").')
    if len(fields) != len(set(fields)):
        raise ValueError("Fields must be unique.")
    if time_limit <= 0:
        raise ValueError("The time limit must be > 0.")
    if time_limit > 3600:
        raise ValueError("The time limit must be <= 3600 (1 hour).")
    if soft_time_limit <= 0:
        raise ValueError("The soft time limit must be > 0.")
    if soft_time_limit > time_limit:
        raise ValueError("The soft time limit must be <= the time limit.")

    # Count the number of digits in the chunk size number.
    chunk_size_digits = len(str(chunk_size))

    # pylint: disable-next=too-many-statements
    def wrapper(get_query_set: t.Callable[..., QuerySet[t.Any]]):
        # Get BigQuery table name and validate it's not already registered.
        _bq_table_name = bq_table_name or get_query_set.__name__
        if _bq_table_name in _BQ_TABLE_NAMES:
            raise ValueError(
                f'The BigQuery table name "{_bq_table_name}" is already'
                "registered."
            )
        _BQ_TABLE_NAMES.add(_bq_table_name)

        # Prefix all CSV files with a folder named after the BiqQuery table.
        bq_table_folder = f"{_bq_table_name}/"

        # Get the runtime settings based on the BigQuery table-write mode.
        if bq_table_write_mode == "append":
            only_list_blobs_in_current_dt_span = True
            delete_blobs_not_in_current_dt_span = False
        else:  # bq_table_write_mode == "overwrite"
            only_list_blobs_in_current_dt_span = False
            delete_blobs_not_in_current_dt_span = True

        # pylint: disable-next=too-many-locals
        def task(*task_args, **task_kwargs):
            # Get the current datetime.
            now = timezone.now()

            # Get the queryset and ensure it has values.
            query_set = get_query_set(*task_args, **task_kwargs)
            if query_set.count() == 0:
                return

            # If the queryset is not ordered, order it by ID by default.
            if not query_set.ordered:
                query_set = query_set.order_by("id")

            # Get the last time this task successfully ran.
            last_run_at = now  # TODO: get real value from DB.

            # Get the range between the last run and now as a formatted string.
            datetime_format = "%Y-%m-%dT%H:%M:%S"
            last_run_at_fstr = last_run_at.strftime(datetime_format)
            now_fstr = now.strftime(datetime_format)

            # Get the default credentials from the environment (Workload Identity Federation)
            # These are the short-lived credentials from the AWS IAM role.
            # creds, _ = default()

            # Create the impersonated credentials object
            # impersonated_creds = impersonated_credentials.Credentials(
            #     source_credentials=creds,
            #     target_principal=(
            #         settings.GOOGLE_CLOUD_STORAGE_SERVICE_ACCOUNT_NAME
            #     ),
            #     # https://cloud.google.com/storage/docs/oauth-scopes
            #     target_scopes=[
            #         "https://www.googleapis.com/auth/devstorage.full_control"
            #     ],
            #     # The lifetime of the impersonated credentials in seconds.
            #     lifetime=time_limit,
            # )

            # Create a client with the impersonated credentials.
            storage_client = gcs.Client()  # (credentials=impersonated_creds)
            bucket = storage_client.bucket(
                settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME
            )

            # List all the existing blobs.
            blobs = t.cast(
                t.Iterator[gcs.Blob],
                bucket.list_blobs(
                    prefix=bq_table_folder
                    + (
                        last_run_at_fstr
                        if only_list_blobs_in_current_dt_span
                        else ""
                    )
                ),
            )

            # Track the name of the last blob in the current datetime span.
            last_blob_name_in_current_dt_span: t.Optional[str] = None
            # Track if found first blob in current datetime span. True by
            # default if only blobs in current datetime are listed.
            found_first_blob_in_current_dt_span = (
                only_list_blobs_in_current_dt_span
            )
            for blob in blobs:
                blob_name = t.cast(str, blob.name)
                # Check if already found first blob in current datetime span.
                if found_first_blob_in_current_dt_span:
                    last_blob_name_in_current_dt_span = blob_name
                # Check if found first blob in current datetime span.
                elif blob_name.startswith(last_run_at_fstr):
                    last_blob_name_in_current_dt_span = blob_name
                # Check if blob not in current datetime span should be deleted.
                elif delete_blobs_not_in_current_dt_span:
                    logging.info('Deleting blob "%s".', blob_name)
                    blob.delete()

            # Get the starting object index. In case of a retry, the index will
            # continue from the index of the last successfully uploaded object.
            object_index = (
                # ...extract the starting object index from its name. E.g.:
                int(
                    # "2025-01-01T00:00:00_2025-01-02T00:00:00__0001_1000.csv"
                    last_blob_name_in_current_dt_span
                    # "2025-01-01T00:00:00_2025-01-02T00:00:00__0001_1000"
                    .removesuffix(".csv")
                    # "1000"
                    .split("_")[-1]
                )
                # If a blob was found...
                if last_blob_name_in_current_dt_span is not None
                # ...else the start with 1st object.
                else 0
            )

            # If the queryset is not starting with the first object, offset it
            # and check there are still values in the queryset.
            if object_index != 0:
                logging.info("Offsetting queryset by %d objects.", object_index)
                query_set = query_set[object_index:]
                if query_set.count() == 0:
                    return

            csv = ""  # Track content of the current CSV file.
            csv_headers = ",".join(fields)  # Headers of each CSV file.

            # Uploads the current CSV file to the GCS bucket.
            def upload_csv():
                # Calculate the current chunk's start and end range.
                chunk_end = str(object_index)
                if object_index == chunk_size:
                    chunk_start = "1".zfill(chunk_size_digits)
                elif object_index < chunk_size:
                    chunk_start = "1".zfill(chunk_size_digits)
                    chunk_end = chunk_end.zfill(chunk_size_digits)
                else:  # object_index > chunk_size
                    chunk_start = str(object_index - chunk_size)

                # Generate the name of the current CSV file based on the
                # datetime range and chunk range.
                csv_path = (
                    bq_table_folder
                    + f"{last_run_at_fstr}_{now_fstr}"
                    + "__"
                    + f"{chunk_start}_{chunk_end}"
                    + ".csv"
                )
                logging.info("Uploading %s to bucket.", csv_path)

                # Create a blob object for the CSV file's path and upload it.
                blob = bucket.blob(csv_path)
                blob.upload_from_string(csv, content_type="text/csv")

            # Iterate through the all the objects in the queryset. The objects
            # are retrieved in chunks (no caching) to avoid OOM errors. For each
            # object, a tuple of values is returned. The order of the values in
            # the tuple is determined by the order of the fields.
            for object_index, values in enumerate(
                t.cast(
                    t.Iterator[t.Tuple[t.Any, ...]],
                    query_set.values_list(*fields).iterator(
                        chunk_size=chunk_size
                    ),
                )
            ):
                # If we've successfully reached the end of the chunk...
                if object_index % chunk_size == 0:
                    # ...upload its CSV (except if it's the 1st object).
                    if object_index != 0:
                        upload_csv()

                    # ...reset the CSV by adding the headers as the 1st row.
                    csv = csv_headers
                # Append the values on a new line.
                csv += "\n" + ",".join(values)

            # Upload the remaining values as a partial chunk.
            upload_csv()

        # Namespace the task with service's name. If the name is not explicitly
        # provided, it defaults to the name of the decorated function.
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
