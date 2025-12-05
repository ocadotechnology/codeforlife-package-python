"""
© Ocado Group
Created on 02/10/2025 at 17:22:38(+01:00).
"""

import os
import typing as t
from datetime import date, datetime, time, timedelta, timezone
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock, patch

from celery import Celery
from django.conf import settings
from django.db.models.query import QuerySet
from google.cloud.bigquery import LoadJobConfig, SourceFormat

from ..tests import CeleryTestCase
from ..types import KwArgs
from ..user.models import User
from .bigquery import BigQueryTask

# pylint: disable=missing-class-docstring


TEST_MODULE = BigQueryTask.__module__


# pylint: disable-next=too-many-instance-attributes,too-many-public-methods
class TestLoadDataIntoBigQueryTask(CeleryTestCase):

    append_users: BigQueryTask
    truncate_users: BigQueryTask

    @staticmethod
    def _get_users():
        return User.objects.all()

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

    # write_queryset_to_csv

    def _test_write_queryset_to_csv(
        self,
        queryset: QuerySet[t.Any],
        fields: t.List[str],
        chunk_size: int = 10,
    ):
        with NamedTemporaryFile(
            mode="w+b", suffix=".csv", delete=True
        ) as csv_file:
            assert queryset.exists() == BigQueryTask.write_queryset_to_csv(
                fields=fields,
                chunk_size=chunk_size,
                queryset=queryset,
                csv_file=csv_file,
            )

            csv_file.seek(0)

            expected_rows = [",".join(fields)] + [
                ",".join(
                    [
                        BigQueryTask.format_value_for_csv(getattr(obj, field))
                        for field in fields
                    ]
                )
                for obj in queryset
            ]

            assert csv_file.read().decode("utf-8") == "\n".join(expected_rows)

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

    def test_shared__table_name_already_registered(self):
        """The append_users task returns a queryset."""
        task = self.append_users
        with self.assert_raises_validation_error(
            code="table_name_already_registered"
        ):
            BigQueryTask.shared(task.settings)(task.get_queryset)

    def _test_shared__write(self, task: BigQueryTask):
        table_name = task.settings.table_name or task.get_queryset.__name__

        mock_bq_client = MagicMock()
        mock_load_table_from_file: MagicMock = (
            mock_bq_client.load_table_from_file
        )

        credentials = "I can haz cheezburger?"

        # pylint: disable-next=consider-using-with
        csv_file = NamedTemporaryFile(mode="w+b", suffix=".csv", delete=False)
        csv_file_name = csv_file.name

        @patch(f"{TEST_MODULE}.Client", return_value=mock_bq_client)
        @patch(
            f"{TEST_MODULE}.get_gcp_service_account_credentials",
            return_value=credentials,
        )
        @patch(f"{TEST_MODULE}.NamedTemporaryFile", return_value=csv_file)
        def test(
            mock_named_temporary_file: MagicMock,
            mock_get_gcp_service_account_credentials: MagicMock,
            mock_bq_client_class: MagicMock,
        ):
            self.apply_task(name=task.name)

            # Assert BigQuery client was created.
            mock_named_temporary_file.assert_called_once_with(
                mode="w+b", suffix=".csv", delete=True
            )
            mock_get_gcp_service_account_credentials.assert_called_once_with(
                token_lifetime_seconds=task.settings.time_limit
            )
            mock_bq_client_class.assert_called_once_with(
                project=settings.GOOGLE_CLOUD_PROJECT_ID,
                credentials=credentials,
            )

            # Assert load_table_from_file was called.
            mock_load_table_from_file.assert_called_once_with(
                file_obj=csv_file,
                destination=".".join(
                    [
                        settings.GOOGLE_CLOUD_PROJECT_ID,
                        settings.GOOGLE_CLOUD_BIGQUERY_DATASET_ID,
                        table_name,
                    ]
                ),
                job_config=LoadJobConfig(
                    source_format=SourceFormat.CSV,
                    skip_leading_rows=1,
                    write_disposition=task.settings.write_disposition,
                    time_zone="Etc/UTC",
                    date_format="YYYY-MM-DD",
                    time_format="HH24:MI:SS",
                    datetime_format="YYYY-MM-DD HH24:MI:SS",
                ),
            )

        try:
            # pylint: disable-next=no-value-for-parameter
            test()
        finally:
            os.remove(csv_file_name)

    def test_shared__write_append(self):
        """The append_users task writes data to BigQuery in append mode."""
        self._test_shared__write(self.append_users)

    def test_shared__write_truncate(self):
        """The append_users task writes data to BigQuery in truncate mode."""
        self._test_shared__write(self.truncate_users)
