"""
© Ocado Group
Created on 06/10/2025 at 17:15:37(+01:00).
"""

import csv
import logging
import typing as t
from dataclasses import dataclass, field
from datetime import date, time, timezone
from tempfile import NamedTemporaryFile

from celery import Task
from celery import shared_task as _shared_task
from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from google.auth import default, impersonated_credentials
from google.cloud import bigquery
from google.oauth2 import service_account

from ..types import KwArgs
from .utils import get_task_name

_TABLE_NAMES: t.Set[str] = set()


# pylint: disable-next=abstract-method
class LoadDataIntoBigQueryTask(Task):
    """A task which loads data from a Django queryset into a BigQuery table."""

    GetQuerySet: t.TypeAlias = t.Callable[..., QuerySet[t.Any]]

    @dataclass(frozen=True)
    # pylint: disable-next=too-many-instance-attributes
    class Settings:
        """The settings for a data warehouse task."""

        # The BigQuery table's write disposition.
        write_disposition: bigquery.WriteDisposition
        # The number of rows to write at a time. Must be a multiple of 10.
        chunk_size: int
        # The [Django model] fields to include in the CSV.
        fields: t.List[str]
        # The name of the field used to identify each object.
        id_field: str = "id"
        # The maximum amount of time this task is allowed to take before it's
        # hard-killed.
        time_limit: int = 3600
        # The name of the BigQuery table where the data will ultimately be
        # saved. If not provided, the name of the decorated function is used.
        table_name: t.Optional[str] = None
        # The maximum number of retries allowed.
        max_retries: int = 5
        # The countdown before attempting the next retry.
        retry_countdown: int = 10
        # The additional keyword arguments to pass to the Celery task decorator.
        kwargs: KwArgs = field(default_factory=dict)

        def __post_init__(self):
            # Set required values as defaults.
            self.kwargs.setdefault("bind", True)
            self.kwargs.setdefault("base", _Task)

            # Ensure the ID field is always present.
            if self.id_field not in self.fields:
                self.fields.append(self.id_field)

            # Validate args.
            if self.chunk_size <= 0:
                raise ValidationError(
                    "The chunk size must be > 0.",
                    code="chunk_size_lte_0",
                )
            if self.chunk_size % 10 != 0:
                raise ValidationError(
                    "The chunk size must be a multiple of 10.",
                    code="chunk_size_not_multiple_of_10",
                )
            if len(self.fields) <= 1:
                raise ValidationError(
                    "Must provide at least 1 field (not including ID field).",
                    code="no_fields",
                )
            if len(self.fields) != len(set(self.fields)):
                raise ValidationError(
                    "Fields must be unique.",
                    code="duplicate_fields",
                )
            if self.time_limit <= 0:
                raise ValidationError(
                    "The time limit must be > 0.",
                    code="time_limit_lte_0",
                )
            if self.time_limit > 3600:
                raise ValidationError(
                    "The time limit must be <= 3600 (1 hour).",
                    code="time_limit_gt_3600",
                )
            if self.max_retries < 0:
                raise ValidationError(
                    "The max retries must be >= 0.",
                    code="max_retries_lt_0",
                )
            if self.retry_countdown < 0:
                raise ValidationError(
                    "The retry countdown must be >= 0.",
                    code="retry_countdown_lt_0",
                )
            if self.kwargs["bind"] is not True:
                raise ValidationError(
                    "The task must be bound.", code="task_unbound"
                )
            if not issubclass(self.kwargs["base"], _Task):
                raise ValidationError(
                    f"The base must be a subclass of "
                    f"'{_Task.__module__}."
                    f"{_Task.__qualname__}'.",
                    code="base_not_subclass",
                )

    settings: Settings
    get_queryset: GetQuerySet

    def _get_bq_client(self):
        # Set the scopes of the credentials.
        # https://cloud.google.com/storage/docs/oauth-scopes
        scopes = ["https://www.googleapis.com/auth/devstorage.full_control"]

        if django_settings.ENV == "local":
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
                target_principal=(),
                target_scopes=scopes,
                # The lifetime of the impersonated credentials in seconds.
                lifetime=self.settings.time_limit,
            )

        # Create a client with the impersonated credentials and get the bucket.
        return bigquery.Client(
            project=django_settings.GOOGLE_CLOUD_PROJECT_ID,
            credentials=credentials,
        )

    @staticmethod
    def write_csv_row(
        writer: "csv.Writer",  # type: ignore[name-defined]
        values: t.Tuple[t.Any, ...],
    ):
        """Write the values to the CSV file in a format BigQuery accepts.

        Args:
            writer: The CSV writer which handles formatting the row.
            values: The values to write to the CSV file.
        """
        # Reimport required to avoid being mocked during testing.
        # pylint: disable-next=reimported,import-outside-toplevel
        from datetime import datetime as _datetime

        # Transform the values into their SQL representations.
        csv_row: t.List[str] = []
        for value in values:
            if value is None:
                value = ""  # BigQuery treats an empty string as NULL/None.
            elif isinstance(value, _datetime):
                value = (
                    value.astimezone(timezone.utc)
                    .replace(tzinfo=None)
                    .isoformat(sep=" ")
                )
            elif isinstance(value, (date, time)):
                value = value.isoformat()
            elif not isinstance(value, str):
                value = str(value)

            csv_row.append(value)

        writer.writerow(csv_row)

    @staticmethod
    # pylint: disable-next=too-many-locals,bad-staticmethod-argument
    def _load_data_into_bq(
        self: "_Task", table_name: str, *task_args, **task_kwargs
    ):
        # Get the queryset.
        queryset = self.get_queryset(*task_args, **task_kwargs)

        # If the queryset is not ordered, order it by ID by default.
        if not queryset.ordered:
            queryset = queryset.order_by(self.settings.id_field)

        with NamedTemporaryFile(
            mode="w+", suffix=".csv", delete=True
        ) as csv_file:
            csv_writer = csv.writer(
                csv_file, lineterminator="\n", quoting=csv.QUOTE_MINIMAL
            )
            csv_writer.writerow(self.settings.fields)  # Write the headers.
            wrote_values = False  # Track if any values were written.

            # Iterate through the all the objects in the queryset. The objects
            # are retrieved in chunks (no caching) to avoid OOM errors. For each
            # object, a tuple of values is returned. The order of the values in
            # the tuple is determined by the order of the fields.
            for chunk_i, values in enumerate(
                t.cast(
                    t.Iterator[t.Tuple[t.Any, ...]],
                    queryset.values_list(*self.settings.fields).iterator(
                        chunk_size=self.settings.chunk_size
                    ),
                )
            ):
                logging.info("Writing chunk index %d to CSV.", chunk_i)
                self.write_csv_row(csv_writer, values)
                wrote_values = True

            if not wrote_values:
                return  # No data to load.

            csv_file.seek(0)  # Reset file pointer to the start.

            logging.info("Starting BigQuery load job.")

            full_table_id = ".".join(
                [
                    django_settings.GOOGLE_CLOUD_PROJECT_ID,
                    django_settings.GOOGLE_CLOUD_BIGQUERY_DATASET_ID,
                    table_name,
                ]
            )

            # Load the temporary CSV file into BigQuery.
            load_job = self._get_bq_client().load_table_from_file(
                file_obj=csv_file,
                destination=full_table_id,
                job_config=bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.CSV,
                    skip_leading_rows=1,
                    write_disposition=self.settings.write_disposition,
                    time_zone="Etc/UTC",
                    date_format="YYYY-MM-DD",
                    time_format="HH24:MI:SS",
                    datetime_format="YYYY-MM-DD HH24:MI:SS",
                ),
            )

            load_job.result()
            logging.info(
                "Successfully loaded %d rows into to BigQuery table %s.",
                load_job.output_rows,
                full_table_id,
            )

    @classmethod
    def shared(cls, settings: Settings):
        """Create a shared data warehouse task.

        This decorator creates a Celery task that saves the queryset

        Each task *must* be given a distinct table name and queryset to avoid
        unintended consequences.

        Examples:
            ```
            @LoadDataIntoBigQueryTask.shared(
                LoadDataIntoBigQueryTask.Settings(
                    # table_name = "example", < explicitly set the table name
                    bq_table_write_mode="append",
                    chunk_size=1000,
                    fields=["first_name", "joined_at", "is_active"],
                )
            )
            def user():  # All users will be saved to a BQ table named "user".
                return User.objects.all()
            ```

        Args:
            settings: The settings for this data warehouse task.

        Returns:
            A wrapper-function which expects to receive a callable that returns
            a queryset and returns a Celery task to save the queryset as CSV
            files in the GCS bucket.
        """

        def wrapper(get_queryset: "_Task.GetQuerySet"):
            # Get the table name and validate it's not already registered.
            table_name = settings.table_name or get_queryset.__name__
            if table_name in _TABLE_NAMES:
                raise ValueError(
                    f'The table name "{table_name}" is already registered.'
                )
            _TABLE_NAMES.add(table_name)

            # Wraps the task with retry logic.
            def task(self: "_Task", *task_args, **task_kwargs):
                try:
                    cls._load_data_into_bq(
                        self, table_name, *task_args, **task_kwargs
                    )
                except Exception as exc:
                    raise self.retry(
                        args=task_args,
                        kwargs=task_kwargs,
                        exc=exc,
                        countdown=settings.retry_countdown,
                    )

            # Namespace the task with service's name. If the name is not
            # explicitly provided, it defaults to the name of the decorated
            # function.
            name = settings.kwargs.pop("name", None)
            name = get_task_name(
                name if isinstance(name, str) else get_queryset
            )

            return t.cast(
                _Task,
                _shared_task(  # type: ignore[call-overload]
                    **settings.kwargs,
                    name=name,
                    time_limit=settings.time_limit,
                    max_retries=settings.max_retries,
                    settings=settings,
                    get_queryset=staticmethod(get_queryset),
                )(task),
            )

        return wrapper


_Task = LoadDataIntoBigQueryTask  # Short alias for type hints.
