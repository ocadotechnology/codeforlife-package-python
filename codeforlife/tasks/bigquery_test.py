"""
© Ocado Group
Created on 02/10/2025 at 17:22:38(+01:00).
"""

import csv
import io
import os
import typing as t
from datetime import date, datetime, time, timedelta, timezone
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock

from celery import Celery
from django.conf import settings
from django.db.models.query import QuerySet
from google.cloud.bigquery import CreateDisposition, SourceFormat

from ..tests import CeleryTestCase
from ..types import KwArgs
from ..user.models import User
from .bigquery import BigQueryTask

if t.TYPE_CHECKING:
    from tempfile import _TemporaryFileWrapper

CsvFile = t.Union[io.BufferedReader, "_TemporaryFileWrapper[bytes]"]

# pylint: disable=missing-class-docstring


# pylint: disable-next=too-many-instance-attributes,too-many-public-methods
class TestLoadDataIntoBigQueryTask(CeleryTestCase):

    append_users: BigQueryTask
    truncate_users: BigQueryTask

    @staticmethod
    def _get_users(order_by: t.Optional[str] = None):
        queryset = User.objects.all()
        if order_by:
            queryset = queryset.order_by(order_by)
        return queryset

    @classmethod
    def setUpClass(cls):
        cls.app = Celery(broker="memory://")

        cls.append_users = BigQueryTask.shared(
            BigQueryTask.Settings(
                table_name="user__append",
                write_disposition=BigQueryTask.WriteDisposition.WRITE_APPEND,
                chunk_size=10,
                fields=["first_name", "is_active"],
            )
        )(cls._get_users)

        cls.truncate_users = BigQueryTask.shared(
            BigQueryTask.Settings(
                table_name="user__truncate",
                write_disposition=BigQueryTask.WriteDisposition.WRITE_TRUNCATE,
                chunk_size=10,
                fields=["first_name", "is_active"],
            )
        )(cls._get_users)

        return super().setUpClass()

    def setUp(self):
        def target(relative_dot_path: str):  # Shortcut for patching.
            return f"{BigQueryTask.__module__}.{relative_dot_path}"

        # Mock creating a NamedTemporaryFile.
        # pylint: disable-next=consider-using-with
        self.csv_file = NamedTemporaryFile(
            mode="w+b", suffix=".csv", delete=False
        )
        self.addCleanup(os.remove, self.csv_file.name)
        self.mock_named_temporary_file = self.patch(
            target("NamedTemporaryFile"), return_value=self.csv_file
        )

        # Mock getting GCP service account credentials.
        self.credentials = "I can haz cheezburger?"
        self.mock_get_gcp_service_account_credentials = self.patch(
            target("get_gcp_service_account_credentials"),
            return_value=self.credentials,
        )

        # Mock BigQuery client and its methods.
        self.mock_bq_client = MagicMock()
        self.mock_bq_client_class = self.patch(
            target("Client"), return_value=self.mock_bq_client
        )

        # Mock load_table_from_file method and its result().
        self.mock_load_table_from_file: MagicMock = (
            self.mock_bq_client.load_table_from_file
        )
        self.mock_load_job = MagicMock()
        self.mock_load_table_from_file.return_value = self.mock_load_job
        self.mock_load_job_result: MagicMock = self.mock_load_job.result
        self.job_config = MagicMock()
        self.mock_load_job_config_class = self.patch(
            target("LoadJobConfig"), return_value=self.job_config
        )

        return super().setUp()

    # assertions

    def _assert_queryset_written_to_csv(
        self,
        queryset: QuerySet[t.Any],
        fields: t.List[str],
        csv_file: t.Optional[CsvFile] = None,
    ):
        # Read the actual CSV content.
        csv_file = csv_file or self.csv_file
        csv_file.seek(0)
        actual_content = csv_file.read().decode("utf-8")

        # Generate the expected CSV content.
        csv_content = io.StringIO()
        csv_writer = csv.writer(
            csv_content, lineterminator="\n", quoting=csv.QUOTE_MINIMAL
        )
        csv_writer.writerow(fields)  # Write the headers.
        for obj in queryset:
            csv_writer.writerow(
                [
                    BigQueryTask.format_value_for_csv(getattr(obj, field))
                    for field in fields
                ]
            )
        expected_content = csv_content.getvalue().rstrip()

        # Assert the actual CSV content matches the expected content.
        assert actual_content == expected_content

    def _assert_csv_file_loaded_into_bigquery(
        self,
        table_name: str,
        token_lifetime_seconds: int,
        write_disposition: str,
        csv_file: CsvFile,
    ):
        # Assert BigQuery client was created.
        self.mock_get_gcp_service_account_credentials.assert_called_once_with(
            token_lifetime_seconds=token_lifetime_seconds
        )
        self.mock_bq_client_class.assert_called_once_with(
            project=settings.GOOGLE_CLOUD_PROJECT_ID,
            credentials=self.credentials,
        )

        # Assert load job was created and run.
        self.mock_load_job_config_class.assert_called_once_with(
            create_disposition=CreateDisposition.CREATE_IF_NEEDED,
            source_format=SourceFormat.CSV,
            skip_leading_rows=1,
            write_disposition=write_disposition,
            time_zone="Etc/UTC",
            date_format="YYYY-MM-DD",
            time_format="HH24:MI:SS",
            datetime_format="YYYY-MM-DD HH24:MI:SS",
        )
        self.mock_load_table_from_file.assert_called_once_with(
            file_obj=csv_file,
            destination=".".join(
                [
                    settings.GOOGLE_CLOUD_PROJECT_ID,
                    settings.GOOGLE_CLOUD_BIGQUERY_DATASET_ID,
                    table_name,
                ]
            ),
            job_config=self.job_config,
        )
        self.mock_load_job_result.assert_called_once_with()

    # settings

    # pylint: disable-next=too-many-arguments
    def _test_settings(
        self,
        code: str,
        write_disposition: str = BigQueryTask.WriteDisposition.WRITE_APPEND,
        chunk_size: int = 10,
        fields: t.Optional[t.List[str]] = None,
        kwargs: t.Optional[KwArgs] = None,
        **settings_kwargs,
    ):
        with self.assert_raises_validation_error(code=code):
            BigQueryTask.Settings(
                write_disposition=write_disposition,
                chunk_size=chunk_size,
                fields=fields or ["some_field"],
                kwargs=kwargs or {},
                **settings_kwargs,
            )

    def test_settings__write_disposition_does_not_exist(self):
        """Write disposition must exist."""
        self._test_settings(
            code="write_disposition_does_not_exist",
            write_disposition="WRITE_INVALID",
        )

    def test_settings__chunk_size_lte_0(self):
        """Chunk size must be > 0."""
        self._test_settings(code="chunk_size_lte_0", chunk_size=0)

    def test_settings__chunk_size_not_multiple_of_10(self):
        """Chunk size must be a multiple of 10."""
        self._test_settings(code="chunk_size_not_multiple_of_10", chunk_size=9)

    def test_settings__no_fields(self):
        """Must provide at least 1 field (not including ID field)."""
        self._test_settings(code="no_fields", fields=["id"])

    def test_settings__duplicate_fields(self):
        """Fields must be unique."""
        self._test_settings(code="duplicate_fields", fields=["email", "email"])

    def test_settings__time_limit_lte_0(self):
        """Time limit must be > 0."""
        self._test_settings(code="time_limit_lte_0", time_limit=0)

    def test_settings__time_limit_gt_3600(self):
        """Time limit must be <= 3600 (1 hour)."""
        self._test_settings(code="time_limit_gt_3600", time_limit=3601)

    def test_settings__max_retries_lt_0(self):
        """Max retries must be >= 0."""
        self._test_settings(code="max_retries_lt_0", max_retries=-1)

    def test_settings__retry_countdown_lt_0(self):
        """Retry countdown must be >= 0."""
        self._test_settings(code="retry_countdown_lt_0", retry_countdown=-1)

    def test_settings__task_unbound(self):
        """BigQueryTask must be bound."""
        self._test_settings(code="task_unbound", kwargs={"bind": False})

    def test_settings__base_not_subclass(self):
        """Base must be a subclass of BigQueryTask."""
        self._test_settings(code="base_not_subclass", kwargs={"base": int})

    # register_table_name

    def test_register_table_name__registered(self):
        """An already registered table name raises a ValidationError."""
        table_name = self.append_users.settings.table_name
        assert table_name
        assert table_name in BigQueryTask.TABLE_NAMES
        with self.assert_raises_validation_error(
            code="table_name_already_registered"
        ):
            BigQueryTask.register_table_name(table_name)

    def test_register_table_name__unregistered(self):
        """An unregistered table name does not raise an error."""
        table_name = "some_unique_table_name"
        assert table_name not in BigQueryTask.TABLE_NAMES
        BigQueryTask.register_table_name(table_name)
        assert table_name in BigQueryTask.TABLE_NAMES

    # format_value_for_csv

    def test_format_value_for_csv__none(self):
        """None is converted to an empty string."""
        assert "" == BigQueryTask.format_value_for_csv(None)

    def test_format_value_for_csv__bool(self):
        """Booleans are converted to 0 or 1."""
        assert "True" == BigQueryTask.format_value_for_csv(True)
        assert "False" == BigQueryTask.format_value_for_csv(False)

    def test_format_value_for_csv__datetime(self):
        """Datetimes are converted to ISO 8601 format with a space separator."""
        assert "2025-02-01 11:30:15" == BigQueryTask.format_value_for_csv(
            datetime(
                year=2025, month=2, day=1, hour=12, minute=30, second=15
            ).replace(tzinfo=timezone(timedelta(hours=1)))
        )

    def test_format_value_for_csv__date(self):
        """Dates are converted to ISO 8601 format."""
        assert "2025-02-01" == BigQueryTask.format_value_for_csv(
            date(year=2025, month=2, day=1)
        )

    def test_format_value_for_csv__time(self):
        """Times are converted to ISO 8601 format, ignoring timezone info."""
        assert "12:30:15" == BigQueryTask.format_value_for_csv(
            time(hour=12, minute=30, second=15)
        )

    # get_ordered_queryset

    def _test_get_ordered_queryset(self, order_by: t.Optional[str] = None):
        task = self.append_users
        queryset = task.get_ordered_queryset(order_by=order_by)
        assert queryset.ordered
        assert list(queryset) == list(
            User.objects.order_by(order_by or task.settings.id_field)
        )

    def test_get_ordered_queryset__pre_ordered(self):
        """Does not reorder an already ordered queryset."""
        self._test_get_ordered_queryset(order_by="first_name")

    def test_get_ordered_queryset__post_ordered(self):
        """Orders the queryset if not already ordered. The default is by ID."""
        self._test_get_ordered_queryset()

    # write_queryset_to_csv

    def _test_write_queryset_to_csv(
        self,
        queryset: QuerySet[t.Any],
        fields: t.List[str],
        chunk_size: int = 10,
    ):
        assert queryset.exists() == BigQueryTask.write_queryset_to_csv(
            fields=fields,
            chunk_size=chunk_size,
            queryset=queryset,
            csv_file=self.csv_file,
        )

        self._assert_queryset_written_to_csv(queryset, fields)

    def test_write_queryset_to_csv__all(self):
        """Values are written to the CSV file."""
        queryset = User.objects.all()
        assert queryset.exists()
        self._test_write_queryset_to_csv(queryset, fields=["first_name"])

    def test_write_queryset_to_csv__none(self):
        """No values are written to the CSV file."""
        queryset = User.objects.none()
        assert not queryset.exists()
        self._test_write_queryset_to_csv(queryset, fields=["first_name"])

    # shared

    def _test_shared__write(self, task: BigQueryTask):
        self.apply_task(name=task.name)

        # Assert CSV file was created.
        self.mock_named_temporary_file.assert_called_once_with(
            mode="w+b", suffix=".csv", delete=True
        )

        # Assert queryset was written to CSV.
        assert self.csv_file.closed
        with open(self.csv_file.name, "rb") as csv_file:
            self._assert_queryset_written_to_csv(
                queryset=task.get_ordered_queryset(),
                fields=task.settings.fields,
                csv_file=csv_file,
            )

        self._assert_csv_file_loaded_into_bigquery(
            table_name=task.settings.table_name or task.get_queryset.__name__,
            token_lifetime_seconds=task.settings.time_limit,
            write_disposition=task.settings.write_disposition,
            csv_file=self.csv_file,
        )

    def test_shared__write_append(self):
        """The append_users task writes data to BigQuery in append mode."""
        self._test_shared__write(self.append_users)

    def test_shared__write_truncate(self):
        """The append_users task writes data to BigQuery in truncate mode."""
        self._test_shared__write(self.truncate_users)
