"""
© Ocado Group
Created on 28/03/2025 at 14:37:46(+00:00).

Custom utilities for Celery tasks.
"""

import logging
import typing as t
from datetime import datetime

from celery import Task
from celery import shared_task as _shared_task
from django.conf import settings
from django.db.models.query import QuerySet
from django.utils import timezone
from google.auth import default, impersonated_credentials
from google.cloud import storage as gcs  # type: ignore[import-untyped]
from google.oauth2 import service_account

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
def save_query_set_as_csvs_in_gcs_bucket(
    bq_table_write_mode: t.Literal["overwrite", "append"],
    chunk_size: int,
    fields: t.List[str],
    time_limit: int = 3600,
    bq_table_name: t.Optional[str] = None,
    max_retries: int = 5,
    retry_countdown: int = 10,
    **kwargs,
):
    # pylint: disable=line-too-long,anomalous-backslash-in-string
    """Create a Celery task that saves a queryset as CSV files in the GCS
    bucket.

    This decorator handles chunking a queryset to avoid out-of-memory (OOM)
    errors. Each chunk is saved as a separate CSV file and follows a naming
    convention that tracks 2 spans:

    1. datetime (dt) - From when this task was last run successfully to now.
    2. object index (obj_i) - The start and end index of the objects.

    The naming convention follows the format:
        **"{dt_start}\_{dt_end}\_\_{i_start}\_{i_end}.csv"**
    The datetime follows the format:
        **"{YYYY}-{MM}-{DD}T{HH}:{MM}:{SS}"** (e.g. "2025-12-01T23:59:59")

    NOTE: The index is padded with zeros to ensure sorting by name is
    consistent. For example, the index span from 1 to 500 would be "001_500".

    Ultimately, these CSV files are imported into a BigQuery table, after which
    they are deleted from the GCS bucket.

    Each task *must* be given a distinct table name and queryset to avoid
    unintended consequences.

    Examples:
        ```
        @save_query_set_as_csvs_in_gcs_bucket(
            # bq_table_name = "example", <- Alternatively, set the table name like so.
            bq_table_write_mode="append",
            chunk_size=1000,
            fields=["first_name", "joined_at", "is_active"],
        )
        def user(): # CSVs will be saved to a BQ table named "user"
            return User.objects.all()
        ```

    Args:
        bq_table_write_mode: The BigQuery table's write-mode.
        chunk_size: The number of objects/rows per CSV. Must be a multiple of 10.
        fields: The [Django model] fields to include in the CSV.
        time_limit: The maximum amount of time this task is allowed to take before it's hard-killed.
        bq_table_name: The name of the BigQuery table where these CSV files will ultimately be imported into. If not provided, the name of the decorated function will be used instead.
        max_retries: The maximum number of retries allowed.
        retry_countdown: The countdown before attempting the next retry.

    Returns:
        A wrapper-function which expects to receive a callable that returns a
        queryset and returns a Celery task to save the queryset as CSV files in
        the GCS bucket.
    """
    # pylint: enable=line-too-long,anomalous-backslash-in-string

    kwargs.setdefault("bind", True)

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
    if max_retries < 0:
        raise ValueError("The max retries must be >= 0.")
    if retry_countdown < 0:
        raise ValueError("The retry countdown must be >= 0.")
    if kwargs["bind"] is not True:
        raise ValueError("The task must bound.")

    # The datetime format used in a CSV name.
    dt_format = "%Y-%m-%dT%H:%M:%S"  # E.g. "2025-01-01T00:00:00"

    class ChunkMetadata(t.NamedTuple):
        """All of the metadata used to track a chunk."""

        dt_start_fstr: str  # datetime span start as formatted string
        dt_end_fstr: str  # datetime span end as formatted string
        obj_i_start: int  # object index span start
        obj_i_end: int  # object index span end
        query_set_count_digits: int  # number of digits in the queryset count

        def to_blob_name(self):
            """Convert this chunk metadata into a blob name."""

            # Left-pad the object indexes with zeros.
            obj_i_start_fstr = str(self.obj_i_start).zfill(
                self.query_set_count_digits
            )
            obj_i_end_fstr = str(self.obj_i_start).zfill(
                self.query_set_count_digits
            )

            # E.g. "2025-01-01T00:00:00_2025-01-02T00:00:00__0001_1000.csv"
            return (
                f"{self.dt_start_fstr}_{self.dt_end_fstr}"
                "__"
                f"{obj_i_start_fstr}_{obj_i_end_fstr}"
                ".csv"
            )

        @classmethod
        def from_blob_name(cls, blob_name: str):
            """Extract the chunk metadata from a blob name."""

            # "2025-01-01T00:00:00_2025-01-02T00:00:00__0001_1000"
            blob_name = blob_name.removesuffix(".csv")

            # "2025-01-01T00:00:00_2025-01-02T00:00:00", "0001_1000"
            dt_span_fstr, obj_i_span_fstr = blob_name.split("__")

            # "2025-01-01T00:00:00", "2025-01-02T00:00:00"
            dt_start_fstr, dt_end_fstr = dt_span_fstr.split("_")
            # "0001", "1000"
            obj_i_start_fstr, obj_i_end_fstr = obj_i_span_fstr.split("_")

            return cls(
                dt_start_fstr=dt_start_fstr,
                dt_end_fstr=dt_end_fstr,
                obj_i_start=int(obj_i_start_fstr),
                obj_i_end=int(obj_i_end_fstr),
                query_set_count_digits=len(obj_i_start_fstr),
            )

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

        # Get the runtime settings based on the BigQuery table's write-mode.
        if bq_table_write_mode == "append":
            only_list_blobs_in_current_dt_span = True
            delete_blobs_not_in_current_dt_span = False
        else:  # bq_table_write_mode == "overwrite"
            only_list_blobs_in_current_dt_span = False
            delete_blobs_not_in_current_dt_span = True

        # pylint: disable-next=too-many-locals
        def _save_query_set_as_csvs_in_gcs_bucket(*task_args, **task_kwargs):
            # Get the current datetime.
            dt_end = timezone.now()

            # Get the queryset.
            query_set = get_query_set(*task_args, **task_kwargs)

            # Ensure there's at least 1 object in the queryset.
            if not query_set.exists():
                return

            # Get the number of digits in the object count within the queryset.
            query_set_count_digits = len(str(query_set.count()))

            # If the queryset is not ordered, order it by ID by default.
            if not query_set.ordered:
                query_set = query_set.order_by("id")

            # Get the last time this task successfully ran.
            dt_start: t.Optional[datetime] = (
                dt_end  # TODO: get real value from DB.
            )

            # Get the range between the last run and now as a formatted string.
            dt_end_fstr = dt_end.strftime(dt_format)
            dt_start_fstr = (
                dt_start.strftime(dt_format) if dt_start else dt_end_fstr
            )

            # Get the default credentials from the environment (Workload Identity Federation)
            # These are the short-lived credentials from the AWS IAM role.
            # creds, _ = default()

            scopes = ["https://www.googleapis.com/auth/devstorage.full_control"]

            creds = service_account.Credentials.from_service_account_file(
                "/workspace/backend/package/service_account.json", scopes=scopes
            )

            # Create the impersonated credentials object
            # impersonated_creds = impersonated_credentials.Credentials(
            #     source_credentials=creds,
            #     target_principal=(
            #         settings.GOOGLE_CLOUD_STORAGE_SERVICE_ACCOUNT_NAME
            #     ),
            #     # https://cloud.google.com/storage/docs/oauth-scopes
            #     target_scopes=scopes,
            #     # The lifetime of the impersonated credentials in seconds.
            #     lifetime=time_limit,
            # )

            # Create a client with the impersonated credentials.
            gcs_client = gcs.Client(credentials=creds)
            bucket = gcs_client.bucket(
                settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME
            )

            # The name of the last blob in the current datetime span.
            last_blob_name_in_current_dt_span: t.Optional[str] = None

            # List all the existing blobs.
            for blob in t.cast(
                t.Iterator[gcs.Blob],
                bucket.list_blobs(
                    prefix=bq_table_folder
                    + (
                        dt_start_fstr
                        if only_list_blobs_in_current_dt_span
                        else ""
                    )
                ),
            ):
                blob_name = t.cast(str, blob.name)

                # Check if found first blob in current datetime span.
                if only_list_blobs_in_current_dt_span or blob_name.startswith(
                    dt_start_fstr
                ):
                    if (
                        query_set_count_digits
                        != ChunkMetadata.from_blob_name(
                            blob_name
                        ).query_set_count_digits
                    ):
                        pass  # TODO: handle renaming blobs

                    last_blob_name_in_current_dt_span = blob_name
                # Check if blob not in current datetime span should be deleted.
                elif delete_blobs_not_in_current_dt_span:
                    logging.info('Deleting blob "%s".', blob_name)
                    blob.delete()

            # Track the current and starting object index (1-based).
            obj_i = obj_i_start = (
                # ...extract the starting object index from its name.
                ChunkMetadata.from_blob_name(
                    last_blob_name_in_current_dt_span
                ).obj_i_end
                + 1
                # If found a blob in the current datetime span...
                if last_blob_name_in_current_dt_span is not None
                else 1  # ...else start with the 1st object.
            )

            # If the queryset is not starting with the first object...
            if obj_i != 1:
                # ...offset the queryset...
                offset = obj_i - 1
                logging.info("Offsetting queryset by %d objects.", offset)
                query_set = query_set[offset:]

                # ...and ensure there's at least 1 object.
                if not query_set.exists():
                    return

            chunk_i = obj_i // chunk_size  # Track chunk index (0-based).
            csv = ""  # Track content of the current CSV file.
            csv_headers = ",".join(fields)  # Headers of each CSV file.

            # Uploads the current CSV file to the GCS bucket.
            def upload_csv(obj_i_end: int):
                # Calculate the starting object index for the current chunk.
                obj_i_start = (chunk_i * chunk_size) + 1

                # Generate the path to the CSV in the bucket.
                csv_path = (
                    bq_table_folder
                    + ChunkMetadata(
                        dt_start_fstr=dt_start_fstr,
                        dt_end_fstr=dt_end_fstr,
                        obj_i_start=obj_i_start,
                        obj_i_end=obj_i_end,
                        query_set_count_digits=query_set_count_digits,
                    ).to_blob_name()
                )
                logging.info("Uploading %s to bucket.", csv_path)

                # Create a blob object for the CSV file's path and upload it.
                blob = bucket.blob(csv_path)
                blob.upload_from_string(csv, content_type="text/csv")

            # Iterate through the all the objects in the queryset. The objects
            # are retrieved in chunks (no caching) to avoid OOM errors. For each
            # object, a tuple of values is returned. The order of the values in
            # the tuple is determined by the order of the fields.
            for obj_i, values in enumerate(
                t.cast(
                    t.Iterator[t.Tuple[t.Any, ...]],
                    query_set.values_list(*fields).iterator(
                        chunk_size=chunk_size
                    ),
                ),
                start=obj_i_start,
            ):
                if obj_i % chunk_size == 1:  # If at the start of a chunk...
                    if obj_i != obj_i_start:  # ...and not the 1st iteration...
                        # ...upload the chunk's CSV and increment its index...
                        upload_csv(obj_i_end=obj_i - 1)
                        chunk_i += 1

                    csv = csv_headers  # ...and start a new CSV.

                # Transform the values into their SQL representations.
                sql_values = [
                    int(value) if isinstance(value, bool) else value
                    for value in values
                ]

                # Append the values on a new line.
                csv += "\n" + ",".join(map(str, sql_values))

            upload_csv(obj_i_end=obj_i)  # Upload final (partial) chunk.

        # Wraps the task with retry logic.
        def task(self: Task, *task_args, **task_kwargs):
            try:
                _save_query_set_as_csvs_in_gcs_bucket(*task_args, **task_kwargs)
            except Exception as exc:
                raise self.retry(exc=exc, countdown=retry_countdown)

        # Namespace the task with service's name. If the name is not explicitly
        # provided, it defaults to the name of the decorated function.
        name = kwargs.pop("name", None)
        name = get_task_name(name if isinstance(name, str) else get_query_set)

        return t.cast(
            "Task[..., t.Any]",
            _shared_task(
                **kwargs,
                name=name,
                time_limit=time_limit,
                max_retries=max_retries,
            )(task),
        )

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
