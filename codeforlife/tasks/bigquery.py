"""
© Ocado Group
Created on 06/10/2025 at 17:15:37(+01:00).
"""

import csv
import io
import logging
import typing as t
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper

from celery import Task
from celery import shared_task as _shared_task
from django.conf import settings as django_settings
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from google.cloud.bigquery import (
    Client,
    CreateDisposition,
    LoadJobConfig,
    SourceFormat,
    WriteDisposition,
)

from ..auth import get_gcp_service_account_credentials
from ..types import KwArgs
from .utils import get_task_name

if t.TYPE_CHECKING:
    CsvFile = _TemporaryFileWrapper[bytes]


# pylint: disable-next=abstract-method
class BigQueryTask(Task):
    """A task which loads data from a Django queryset into a BigQuery table."""

    TABLE_NAMES: t.Set[str] = set()

    WriteDisposition: t.TypeAlias = WriteDisposition  # shorthand
    GetQuerySet: t.TypeAlias = t.Callable[..., QuerySet[t.Any]]

    @dataclass(frozen=True)
    # pylint: disable-next=too-many-instance-attributes
    class Settings:
        """The settings for a BigQuery task."""

        # The BigQuery table's write disposition.
        write_disposition: str
        # The number of rows to write at a time. Must be a multiple of 10.
        chunk_size: int
        # The [Django model] fields to include in the CSV.
        fields: t.List[str]
        # The name of the field used to identify each row.
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
            self.kwargs.setdefault("base", BigQueryTask)

            # Ensure the ID field is always present.
            if self.id_field not in self.fields:
                self.fields.append(self.id_field)

            # Validate args.
            if not self.write_disposition.startswith("WRITE_") or not hasattr(
                WriteDisposition, self.write_disposition
            ):
                raise ValidationError(
                    f'The write disposition "{self.write_disposition}"'
                    " does not exist.",
                    code="write_disposition_does_not_exist",
                )
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
            if not issubclass(self.kwargs["base"], BigQueryTask):
                raise ValidationError(
                    f"The base must be a subclass of "
                    f"'{BigQueryTask.__module__}."
                    f"{BigQueryTask.__qualname__}'.",
                    code="base_not_subclass",
                )

    settings: Settings
    get_queryset: GetQuerySet

    @classmethod
    def register_table_name(cls, table_name: str):
        """Register a table name to ensure it is unique.

        Args:
            table_name: The name of the table to register.

        Raises:
            ValidationError: If the table name is already registered.
        """

        if table_name in cls.TABLE_NAMES:
            raise ValidationError(
                f'The table name "{table_name}" is already registered.',
                code="table_name_already_registered",
            )

        cls.TABLE_NAMES.add(table_name)

    def get_ordered_queryset(self, *task_args, **task_kwargs):
        """Get the ordered queryset.

        Args:
            task_args: The positional arguments passed to the task.
            task_kwargs: The keyword arguments passed to the task.

        Returns:
            The ordered queryset.
        """

        queryset = self.get_queryset(*task_args, **task_kwargs)
        if not queryset.ordered:
            queryset = queryset.order_by(self.settings.id_field)

        return queryset

    @staticmethod
    def format_value_for_csv(value: t.Any) -> str:
        """Format a value for inclusion in a CSV file.

        Args:
            value: The value to format.

        Returns:
            The formatted value as a string.
        """

        if value is None:
            return ""  # BigQuery treats an empty string as NULL/None.
        if isinstance(value, datetime):
            return (
                value.astimezone(timezone.utc)
                .replace(tzinfo=None)
                .isoformat(sep=" ")
            )
        if isinstance(value, (date, time)):
            return value.isoformat()
        if not isinstance(value, str):
            return str(value)

        return value

    @classmethod
    def write_queryset_to_csv(
        cls,
        fields: t.List[str],
        chunk_size: int,
        queryset: QuerySet[t.Any],
        csv_file: "CsvFile",
    ):
        """Write a queryset to a CSV file.

        Args:
            fields: The list of fields to include in the CSV.
            chunk_size: The number of rows to write at a time.
            queryset: The queryset to write.
            csv_file: The CSV file to write to.

        Returns:
            Whether any values were written to the CSV file.
        """

        text_wrapper = io.TextIOWrapper(csv_file, encoding="utf-8", newline="")

        csv_writer = csv.writer(
            text_wrapper, lineterminator="\n", quoting=csv.QUOTE_MINIMAL
        )
        csv_writer.writerow(fields)  # Write the headers.

        chunk_index = 1  # 1 based index. For logging.
        wrote_values = False  # Track if any values were written.

        for row_index, values in enumerate(
            t.cast(
                t.Iterator[t.Tuple[t.Any, ...]],
                # Iterate chunks to avoid OOM for large querysets.
                queryset.values_list(*fields).iterator(chunk_size),
            )
        ):
            if row_index % chunk_size == 0:
                logging.info("Writing chunk %d", chunk_index)
                chunk_index += 1

            csv_row = [cls.format_value_for_csv(value) for value in values]
            csv_writer.writerow(csv_row)
            wrote_values = True

        # Move back 1 byte (because lineterminator is "\n").
        text_wrapper.seek(text_wrapper.tell() - 1)
        # Chop off the trailing newline.
        text_wrapper.truncate()
        # Detach the wrapper to flush data to the binary file.
        text_wrapper.detach()

        return wrote_values

    @staticmethod
    def load_csv_into_bq(
        write_disposition: str,
        time_limit: int,
        table_name: str,
        csv_file: "CsvFile",
    ):
        """Load a CSV file into a BigQuery table.

        Args:
            write_disposition: Write disposition for the BigQuery table.
            time_limit: The maximum time to wait for the load job to complete.
            table_name: The table name in BigQuery.
            csv_file: The CSV file to load into BigQuery.
        """

        bq_client = Client(
            project=django_settings.GOOGLE_CLOUD_PROJECT_ID,
            credentials=get_gcp_service_account_credentials(
                token_lifetime_seconds=time_limit
            ),
        )

        full_table_id = ".".join(
            [
                django_settings.GOOGLE_CLOUD_PROJECT_ID,
                django_settings.GOOGLE_CLOUD_BIGQUERY_DATASET_ID,
                table_name,
            ]
        )

        csv_file.seek(0)  # Reset file pointer to the start.

        logging.info("Starting BigQuery load job.")
        # Load the temporary CSV file into BigQuery.
        bq_load_job = bq_client.load_table_from_file(
            file_obj=csv_file,
            destination=full_table_id,
            job_config=LoadJobConfig(
                create_disposition=CreateDisposition.CREATE_IF_NEEDED,
                source_format=SourceFormat.CSV,
                skip_leading_rows=1,
                write_disposition=write_disposition,
                time_zone="Etc/UTC",
                date_format="YYYY-MM-DD",
                time_format="HH24:MI:SS",
                datetime_format="YYYY-MM-DD HH24:MI:SS",
            ),
        )

        bq_load_job.result()
        logging.info(
            "Successfully loaded %d rows into to BigQuery table %s.",
            bq_load_job.output_rows,
            full_table_id,
        )

    @staticmethod
    # pylint: disable-next=too-many-locals,bad-staticmethod-argument
    def _load_data_into_bq(
        self: "BigQueryTask", table_name: str, *task_args, **task_kwargs
    ):
        queryset = self.get_ordered_queryset(*task_args, **task_kwargs)

        with NamedTemporaryFile(
            mode="w+b", suffix=".csv", delete=True
        ) as csv_file:
            if self.write_queryset_to_csv(
                fields=self.settings.fields,
                chunk_size=self.settings.chunk_size,
                queryset=queryset,
                csv_file=csv_file,
            ):
                self.load_csv_into_bq(
                    write_disposition=self.settings.write_disposition,
                    time_limit=self.settings.time_limit,
                    table_name=table_name,
                    csv_file=csv_file,
                )

    @classmethod
    def shared(cls, settings: Settings):
        """Create a shared BigQuery task.

        This decorator creates a Celery task that saves the queryset to a
        BigQuery table.

        Each task *must* be given a distinct table name and queryset to avoid
        unintended consequences.

        Examples:
        ```
        @BigQueryTask.shared(
            BigQueryTask.Settings(
                # table_name = "example", <- explicitly set the table name
                write_disposition=BigQueryTask.WriteDisposition.WRITE_TRUNCATE,
                chunk_size=1000,
                fields=["first_name", "joined_at", "is_active"],
            )
        )
        def user():  # All users will be saved to a BQ table named "user".
            return User.objects.all()
        ```

        Args:
            settings: The settings for this BigQuery task.

        Returns:
            A wrapper-function which expects to receive a callable that returns
            a queryset and returns a Celery task to save the queryset to
            BigQuery.
        """

        def wrapper(get_queryset: "BigQueryTask.GetQuerySet"):
            table_name = settings.table_name or get_queryset.__name__
            cls.register_table_name(table_name)

            # Wraps the task with retry logic.
            def task(self: "BigQueryTask", *task_args, **task_kwargs):
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
                BigQueryTask,
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
