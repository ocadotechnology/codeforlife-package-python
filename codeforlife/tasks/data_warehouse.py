"""
© Ocado Group
Created on 06/10/2025 at 17:15:37(+01:00).
"""

import logging
import typing as t
from datetime import datetime, timezone
from functools import cached_property

from celery import Task
from celery import shared_task as _shared_task
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from google.auth import default, impersonated_credentials
from google.cloud import storage as gcs  # type: ignore[import-untyped]
from google.oauth2 import service_account

from .utils import get_task_name

_BQ_TABLE_NAMES: t.Set[str] = set()


# pylint: disable-next=abstract-method
class DataWarehouseTask(Task):
    """A task that saves a queryset as CSV files in the GCS bucket."""

    GetQuerySet: t.TypeAlias = t.Callable[..., QuerySet[t.Any]]

    # pylint: disable-next=too-many-instance-attributes
    class Options:
        """The options for a data warehouse task."""

        BqTableWriteMode: t.TypeAlias = t.Literal["overwrite", "append"]

        # pylint: disable-next=too-many-arguments,too-many-branches
        def __init__(
            self,
            bq_table_write_mode: BqTableWriteMode,
            chunk_size: int,
            fields: t.List[str],
            time_limit: int = 3600,
            bq_table_name: t.Optional[str] = None,
            max_retries: int = 5,
            retry_countdown: int = 10,
            **kwargs,
        ):
            # pylint: disable=line-too-long
            """Create the options for a data warehouse task.

            Args:
                bq_table_write_mode: The BigQuery table's write-mode.
                chunk_size: The number of objects/rows per CSV. Must be a multiple of 10.
                fields: The [Django model] fields to include in the CSV.
                time_limit: The maximum amount of time this task is allowed to take before it's hard-killed.
                bq_table_name: The name of the BigQuery table where these CSV files will ultimately be imported into. If not provided, the name of the decorated function will be used instead.
                max_retries: The maximum number of retries allowed.
                retry_countdown: The countdown before attempting the next retry.
            """
            # pylint: enable=line-too-long

            # Set required values as defaults.
            kwargs.setdefault("bind", True)
            kwargs.setdefault("base", DataWarehouseTask)

            # Ensure the ID field is always present.
            if "id" not in fields:
                fields.append("id")

            # Validate args.
            if chunk_size <= 0:
                raise ValidationError(
                    "The chunk size must be > 0.",
                    code="chunk_size_lte_0",
                )
            if chunk_size % 10 != 0:
                raise ValidationError(
                    "The chunk size must be a multiple of 10.",
                    code="chunk_size_not_multiple_of_10",
                )
            if len(fields) <= 1:
                raise ValidationError(
                    'Must provide at least 1 field (not including "id").',
                    code="no_fields",
                )
            if len(fields) != len(set(fields)):
                raise ValidationError(
                    "Fields must be unique.",
                    code="duplicate_fields",
                )
            if time_limit <= 0:
                raise ValidationError(
                    "The time limit must be > 0.",
                    code="time_limit_lte_0",
                )
            if time_limit > 3600:
                raise ValidationError(
                    "The time limit must be <= 3600 (1 hour).",
                    code="time_limit_gt_3600",
                )
            if max_retries < 0:
                raise ValidationError(
                    "The max retries must be >= 0.",
                    code="max_retries_lt_0",
                )
            if retry_countdown < 0:
                raise ValidationError(
                    "The retry countdown must be >= 0.",
                    code="retry_countdown_lt_0",
                )
            if kwargs["bind"] is not True:
                raise ValidationError(
                    "The task must bound.", code="task_unbound"
                )
            if not issubclass(kwargs["base"], DataWarehouseTask):
                raise ValidationError(
                    f"The base must be a subclass of "
                    f"'{DataWarehouseTask.__module__}."
                    f"{DataWarehouseTask.__qualname__}'.",
                    code="base_not_subclass",
                )

            self._bq_table_write_mode = bq_table_write_mode
            self._chunk_size = chunk_size
            self._fields = fields
            self._time_limit = time_limit
            self._bq_table_name = bq_table_name
            self._max_retries = max_retries
            self._retry_countdown = retry_countdown
            self._kwargs = kwargs

            # Get the runtime settings based on the BigQuery table's write-mode.
            if bq_table_write_mode == "append":
                self._only_list_blobs_from_current_timestamp = True
                self._delete_blobs_not_from_current_timestamp = False
            else:  # bq_table_write_mode == "overwrite"
                self._only_list_blobs_from_current_timestamp = False
                self._delete_blobs_not_from_current_timestamp = True

        @property
        def bq_table_write_mode(self):
            """The BigQuery table's write-mode."""
            return self._bq_table_write_mode

        @property
        def chunk_size(self):
            """The number of objects/rows per CSV. Must be a multiple of 10."""
            return self._chunk_size

        @property
        def fields(self):
            """The [Django model] fields to include in the CSV."""
            return self._fields

        @cached_property
        def csv_headers(self):
            """The headers of each CSV file."""
            return ",".join(self._fields)

        @property
        def time_limit(self):
            """
            The maximum amount of time this task is allowed to take before it's
            hard-killed.
            """
            return self._time_limit

        @property
        def bq_table_name(self):
            """
            The name of the BigQuery table where the CSV files will ultimately
            be imported into.
            """
            return self._bq_table_name

        @property
        def max_retries(self):
            """The maximum number of retries allowed."""
            return self._max_retries

        @property
        def retry_countdown(self):
            """The countdown before attempting the next retry."""
            return self._retry_countdown

        @property
        def only_list_blobs_from_current_timestamp(self):
            """Whether to only list blobs from the current timestamp."""
            return self._only_list_blobs_from_current_timestamp

        @property
        def delete_blobs_not_from_current_timestamp(self):
            """Whether to delete all blobs not from the current timestamp."""
            return self._delete_blobs_not_from_current_timestamp

    options: Options
    get_queryset: GetQuerySet

    class ChunkMetadata(t.NamedTuple):
        """All of the metadata used to track a chunk."""

        bq_table_name: str  # the name of the BigQuery table
        timestamp: str  # when the task was first run
        obj_i_start: int  # object index span start
        obj_i_end: int  # object index span end
        obj_count_digits: int  # number of digits in the object count

        def to_blob_name(self):
            """Convert this chunk metadata into a blob name."""

            # Left-pad the object indexes with zeros.
            obj_i_start_fstr = str(self.obj_i_start).zfill(
                self.obj_count_digits
            )
            obj_i_end_fstr = str(self.obj_i_end).zfill(self.obj_count_digits)

            # E.g. "user/2025-01-01_00:00:00__0001_1000.csv"
            return (
                f"{self.bq_table_name}/{self.timestamp}__"
                f"{obj_i_start_fstr}_{obj_i_end_fstr}.csv"
            )

        @classmethod
        def from_blob_name(cls, blob_name: str):
            """Extract the chunk metadata from a blob name."""

            # E.g. "user/2025-01-01_00:00:00__0001_1000.csv"
            # "2025-01-01_00:00:00__0001_1000.csv"
            bq_table_name, blob_name = blob_name.split("/", maxsplit=1)
            # "2025-01-01_00:00:00__0001_1000"
            blob_name = blob_name.removesuffix(".csv")
            # "2025-01-01_00:00:00", "0001_1000"
            timestamp, obj_i_span_fstr = blob_name.split("__")
            # "0001", "1000"
            obj_i_start_fstr, obj_i_end_fstr = obj_i_span_fstr.split("_")

            return cls(
                bq_table_name=bq_table_name,
                timestamp=timestamp,
                obj_i_start=int(obj_i_start_fstr),
                obj_i_end=int(obj_i_end_fstr),
                obj_count_digits=len(obj_i_start_fstr),
            )

    def _get_gcs_bucket(self):
        # Set the scopes of the credentials.
        # https://cloud.google.com/storage/docs/oauth-scopes
        scopes = ["https://www.googleapis.com/auth/devstorage.full_control"]

        if settings.ENV == "local":
            # Load the credentials from a local JSON file.
            credentials = service_account.Credentials.from_service_account_file(
                "/replace/me/with/path/to/service_account.json",
                scopes=scopes,
            )
        else:
            # Use Workload Identity Federation to get the default credentials
            # from the environment. These are the short-lived credentials from
            # the AWS IAM role.
            source_credentials, _ = default()

            # Create the impersonated credentials object
            credentials = impersonated_credentials.Credentials(
                source_credentials=source_credentials,
                target_principal=(
                    settings.GOOGLE_CLOUD_STORAGE_SERVICE_ACCOUNT_NAME
                ),
                target_scopes=scopes,
                # The lifetime of the impersonated credentials in seconds.
                lifetime=self.options.time_limit,
            )

        # Create a client with the impersonated credentials and get the bucket.
        return gcs.Client(credentials=credentials).bucket(
            settings.GOOGLE_CLOUD_STORAGE_BUCKET_NAME
        )

    @staticmethod
    def format_values(values: t.Tuple[t.Any, ...]):
        """Format the values as a newline in a CSV file."""
        # Transform the values into their SQL representations.
        sql_values: t.List[str] = []
        for value in values:
            if isinstance(value, bool):
                value = int(value)

            sql_values.append(str(value))

        # Append the values on a new line.
        return "\n" + ",".join(sql_values)

    @staticmethod
    def to_timestamp(dt: datetime):
        """
        Formats a datetime to a timestamp to be used in a CSV name.
        E.g. "2025-01-01_00:00:00"
        """
        return dt.strftime("%Y-%m-%d_%H:%M:%S")

    @staticmethod
    # pylint: disable-next=too-many-locals,bad-staticmethod-argument
    def _save_query_set_as_csvs_in_gcs_bucket(
        self: "DataWarehouseTask", timestamp: str, *task_args, **task_kwargs
    ):
        # Get the queryset.
        queryset = self.get_queryset(*task_args, **task_kwargs)

        # Count the objects in the queryset and ensure there's at least 1.
        obj_count = queryset.count()
        if obj_count == 0:
            return

        # Get the number of digits in the object count.
        obj_count_digits = len(str(obj_count))

        # If the queryset is not ordered, order it by ID by default.
        if not queryset.ordered:
            queryset = queryset.order_by("id")

        # Limit the queryset to the object count to ensure the number of
        # digits in the count remains consistent.
        queryset = queryset[:obj_count]

        # Impersonate the service account and get access to the GCS bucket.
        bucket = self._get_gcs_bucket()

        # The name of the last blob from the current timestamp.
        last_blob_name_from_current_timestamp: t.Optional[str] = None

        # List all the existing blobs.
        for blob in t.cast(
            t.Iterator[gcs.Blob],
            bucket.list_blobs(
                prefix=f"{self.options.bq_table_name}/"
                + (
                    timestamp
                    if self.options.only_list_blobs_from_current_timestamp
                    else ""
                )
            ),
        ):
            blob_name = t.cast(str, blob.name)

            # Check if found first blob from current timestamp.
            if (
                self.options.only_list_blobs_from_current_timestamp
                or blob_name.startswith(timestamp)
            ):
                chunk_metadata = self.ChunkMetadata.from_blob_name(blob_name)

                # If the number of digits in the object count has changed...
                if obj_count_digits != chunk_metadata.obj_count_digits:
                    # ...update the number of digits in the object count...
                    chunk_metadata.obj_count_digits = obj_count_digits
                    # ...and update the blob name...
                    blob_name = chunk_metadata.to_blob_name()
                    # ...and copy the blob with the updated name...
                    bucket.copy_blob(
                        blob=blob,
                        destination_bucket=bucket,
                        new_name=blob_name,
                    )
                    # ...and delete the old blob.
                    logging.info('Deleting blob "%s".', blob.name)
                    blob.delete()

                last_blob_name_from_current_timestamp = blob_name
            # Check if blobs not from the current timestamp should be deleted.
            elif self.options.delete_blobs_not_from_current_timestamp:
                logging.info('Deleting blob "%s".', blob_name)
                blob.delete()

        # Track the current and starting object index (1-based).
        obj_i = obj_i_start = (
            # ...extract the starting object index from its name.
            self.ChunkMetadata.from_blob_name(
                last_blob_name_from_current_timestamp
            ).obj_i_end
            + 1
            # If found a blob from the current timestamp...
            if last_blob_name_from_current_timestamp is not None
            else 1  # ...else start with the 1st object.
        )

        # If the queryset is not starting with the first object...
        if obj_i != 1:
            # ...offset the queryset...
            offset = obj_i - 1
            logging.info("Offsetting queryset by %d objects.", offset)
            queryset = queryset[offset:]

            # ...and ensure there's at least 1 object.
            if not queryset.exists():
                return

        chunk_i = obj_i // self.options.chunk_size  # Chunk index (0-based).
        csv = ""  # Track content of the current CSV file.

        # Uploads the current CSV file to the GCS bucket.
        def upload_csv(obj_i_end: int):
            # Calculate the starting object index for the current chunk.
            obj_i_start = (chunk_i * self.options.chunk_size) + 1

            # Generate the path to the CSV in the bucket.
            blob_name = self.ChunkMetadata(
                bq_table_name=self.options.bq_table_name,
                timestamp=timestamp,
                obj_i_start=obj_i_start,
                obj_i_end=obj_i_end,
                obj_count_digits=obj_count_digits,
            ).to_blob_name()

            # Create a blob object for the CSV file's path and upload it.
            logging.info("Uploading %s to bucket.", blob_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(csv, content_type="text/csv")

        # Iterate through the all the objects in the queryset. The objects
        # are retrieved in chunks (no caching) to avoid OOM errors. For each
        # object, a tuple of values is returned. The order of the values in
        # the tuple is determined by the order of the fields.
        for obj_i, values in enumerate(
            t.cast(
                t.Iterator[t.Tuple[t.Any, ...]],
                queryset.values_list(*self.options.fields).iterator(
                    chunk_size=self.options.chunk_size
                ),
            ),
            start=obj_i_start,
        ):
            if obj_i % self.options.chunk_size == 1:  # If start of a chunk...
                if obj_i != obj_i_start:  # ...and not the 1st iteration...
                    # ...upload the chunk's CSV and increment its index...
                    upload_csv(obj_i_end=obj_i - 1)
                    chunk_i += 1

                csv = self.options.csv_headers  # ...and start a new CSV.

            # Append the values on a new line.
            csv += self.format_values(values)

        upload_csv(obj_i_end=obj_i)  # Upload final (maybe partial) chunk.

    @classmethod
    def shared(cls, options: Options):
        # pylint: disable=line-too-long,anomalous-backslash-in-string
        """Create a Celery task that saves a queryset as CSV files in the GCS
        bucket.

        This decorator handles chunking a queryset to avoid out-of-memory (OOM)
        errors. Each chunk is saved as a separate CSV file and follows a naming
        convention that tracks 2 dimensions:

        1. timestamp - When this task first ran (in case of retries).
        2. object index (obj_i) - The start and end index of the objects.

        The naming convention follows the format:
            **"{timestamp}\_\_{i_start}\_{i_end}.csv"**
        The timestamp follows the format:
            **"{YYYY}-{MM}-{DD}_{HH}:{MM}:{SS}"** (e.g. "2025-12-01_23:59:59")

        NOTE: The index is padded with zeros to ensure sorting by name is
        consistent. For example, the index span from 1 to 500 would be "001_500".

        Ultimately, these CSV files are imported into a BigQuery table, after which
        they are deleted from the GCS bucket.

        Each task *must* be given a distinct table name and queryset to avoid
        unintended consequences.

        Examples:
            ```
            @DataWarehouseTask.shared(
                DataWarehouseTask.Options(
                    # bq_table_name = "example", <- Alternatively, set the table name like so.
                    bq_table_write_mode="append",
                    chunk_size=1000,
                    fields=["first_name", "joined_at", "is_active"],
                )
            )
            def user(): # CSVs will be saved to a BQ table named "user"
                return User.objects.all()
            ```

        Args:
            options: The options for this data warehouse task.

        Returns:
            A wrapper-function which expects to receive a callable that returns a
            queryset and returns a Celery task to save the queryset as CSV files in
            the GCS bucket.
        """
        # pylint: enable=line-too-long,anomalous-backslash-in-string

        def wrapper(get_queryset: "DataWarehouseTask.GetQuerySet"):
            # Get BigQuery table name and validate it's not already registered.
            bq_table_name = options.bq_table_name or get_queryset.__name__
            if bq_table_name in _BQ_TABLE_NAMES:
                raise ValueError(
                    f'The BigQuery table name "{bq_table_name}" is already'
                    "registered."
                )
            _BQ_TABLE_NAMES.add(bq_table_name)

            # Overwrite BigQuery table name.
            # pylint: disable-next=protected-access
            options._bq_table_name = bq_table_name

            # Wraps the task with retry logic.
            def task(self: "DataWarehouseTask", *task_args, **task_kwargs):
                timestamp = (
                    # ...get the current timestamp.
                    self.to_timestamp(datetime.now(timezone.utc))
                    # If this is the first run...
                    if self.request.retries == 0
                    # ...else pop the timestamp passed from the first run.
                    else t.cast(str, task_kwargs.pop("_timestamp"))
                )

                try:
                    cls._save_query_set_as_csvs_in_gcs_bucket(
                        self, timestamp, *task_args, **task_kwargs
                    )
                except Exception as exc:
                    raise self.retry(
                        args=task_args,
                        # Pass the timestamp from the first run to the retry.
                        kwargs={**task_kwargs, "_timestamp": timestamp},
                        exc=exc,
                        countdown=options.retry_countdown,
                    )

            # pylint: disable-next=protected-access
            kwargs = options._kwargs

            # Namespace the task with service's name. If the name is not
            # explicitly provided, it defaults to the name of the decorated
            # function.
            name = kwargs.pop("name", None)
            name = get_task_name(
                name if isinstance(name, str) else get_queryset
            )

            return t.cast(
                DataWarehouseTask,
                _shared_task(  # type: ignore[call-overload]
                    **kwargs,
                    name=name,
                    time_limit=options.time_limit,
                    max_retries=options.max_retries,
                    options=options,
                    get_queryset=staticmethod(get_queryset),
                )(task),
            )

        return wrapper
