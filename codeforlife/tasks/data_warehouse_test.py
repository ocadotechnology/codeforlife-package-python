"""
© Ocado Group
Created on 02/10/2025 at 17:22:38(+01:00).
"""

import csv
import io
import typing as t
from datetime import date, datetime, time, timedelta, timezone
from unittest.mock import MagicMock, call, patch

from celery import Celery

from ..tests import CeleryTestCase
from ..types import Args, KwArgs
from ..user.models import User
from .data_warehouse import DataWarehouseTask as DWT

# pylint: disable=missing-class-docstring


@DWT.shared(
    DWT.Settings(
        bq_table_name="user__append",
        bq_table_write_mode="append",
        chunk_size=10,
        fields=["first_name", "is_active"],
    )
)
def append_users():
    """Append all users in the "user__append" BigQuery table."""
    return User.objects.all()


@DWT.shared(
    DWT.Settings(
        bq_table_name="user__overwrite",
        bq_table_write_mode="overwrite",
        chunk_size=10,
        fields=["first_name", "is_active"],
    )
)
def overwrite_users():
    """Overwrite all users in the "user__overwrite" BigQuery table."""
    return User.objects.all()


class MockGcsBlob:
    def __init__(self, chunk_metadata: DWT.ChunkMetadata):
        self.chunk_metadata = chunk_metadata
        self.upload_from_string = MagicMock()
        self.delete = MagicMock()

    @property
    def name(self):
        """The name of the blob."""
        return self.chunk_metadata.to_blob_name()

    def __repr__(self):
        return self.name

    @classmethod
    # pylint: disable-next=too-many-arguments
    def generate_list(
        cls,
        task: DWT,
        timestamp: str,
        obj_i_start: int,
        obj_i_end: int,
        obj_count_digits: int,
    ):
        """Generate a list of mock GCS blobs.

        Args:
            task: The task that produced these blobs.
            timestamp: When the task first ran.
            obj_i_start: The object index span start.
            obj_i_end: The object index span end.
            obj_count_digits: The number of digits in the object count

        Returns:
            A list of mock GCS blobs.
        """
        return [
            cls(
                chunk_metadata=DWT.ChunkMetadata(
                    bq_table_name=task.settings.bq_table_name,
                    timestamp=timestamp,
                    obj_i_start=obj_i_start,
                    obj_i_end=min(
                        obj_i_start + task.settings.chunk_size - 1, obj_i_end
                    ),
                    obj_count_digits=obj_count_digits,
                )
            )
            for obj_i_start in range(
                obj_i_start, obj_i_end + 1, task.settings.chunk_size
            )
        ]


# pylint: disable-next=too-few-public-methods
class MockGcsBucket:
    def __init__(
        self,
        list_blobs_return: t.List[MockGcsBlob],
        new_blobs: t.List[MockGcsBlob],
    ):
        self.list_blobs = MagicMock(return_value=list_blobs_return)
        self.blob = MagicMock(side_effect=new_blobs)  # Returns 1 blob per call.
        self.copy_blob = MagicMock()


# pylint: disable-next=too-many-instance-attributes,too-many-public-methods
class TestDataWarehouseTask(CeleryTestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = Celery(broker="memory://")

        return super().setUpClass()

    def setUp(self):
        self.date = date(year=2025, month=2, day=1)
        self.time = time(hour=12, minute=30, second=15)
        self.datetime = datetime.combine(self.date, self.time)

        self.bq_table_name = "example"
        self.timestamp = DWT.to_timestamp(self.datetime)
        self.obj_i_start = 1
        self.obj_i_end = 100
        self.obj_count_digits = 4

        obj_i_start_fstr = str(self.obj_i_start).zfill(self.obj_count_digits)
        obj_i_end_fstr = str(self.obj_i_end).zfill(self.obj_count_digits)

        self.blob_name = (
            f"{self.bq_table_name}/{self.timestamp}__"
            f"{obj_i_start_fstr}_{obj_i_end_fstr}.csv"
        )

        return super().setUp()

    # Options

    def _test_options(
        self,
        code: str,
        bq_table_write_mode: DWT.Settings.BqTableWriteMode = ("append"),
        chunk_size: int = 10,
        fields: t.Optional[t.List[str]] = None,
        **kwargs,
    ):
        with self.assert_raises_validation_error(code=code):
            DWT.Settings(
                bq_table_write_mode=bq_table_write_mode,
                chunk_size=chunk_size,
                fields=fields or ["some_field"],
                **kwargs,
            )

    def test_options__chunk_size_lte_0(self):
        """Chunk size must be > 0."""
        self._test_options(code="chunk_size_lte_0", chunk_size=0)

    def test_options__chunk_size_not_multiple_of_10(self):
        """Chunk size must be a multiple of 10."""
        self._test_options(code="chunk_size_not_multiple_of_10", chunk_size=9)

    def test_options__no_fields(self):
        """Must provide at least 1 field (not including "id")."""
        self._test_options(code="no_fields", fields=["id"])

    def test_options__duplicate_fields(self):
        """Fields must be unique."""
        self._test_options(code="duplicate_fields", fields=["email", "email"])

    def test_options__time_limit_lte_0(self):
        """Time limit must be > 0."""
        self._test_options(code="time_limit_lte_0", time_limit=0)

    def test_options__time_limit_gt_3600(self):
        """Time limit must be <= 3600 (1 hour)."""
        self._test_options(code="time_limit_gt_3600", time_limit=3601)

    def test_options__max_retries_lt_0(self):
        """Max retries must be >= 0."""
        self._test_options(code="max_retries_lt_0", max_retries=-1)

    def test_options__retry_countdown_lt_0(self):
        """Retry countdown must be >= 0."""
        self._test_options(code="retry_countdown_lt_0", retry_countdown=-1)

    def test_options__task_unbound(self):
        """Task must be bound."""
        self._test_options(code="task_unbound", bind=False)

    def test_options__base_not_subclass(self):
        """Base must be a subclass of DWT."""
        self._test_options(code="base_not_subclass", base=int)

    # To timestamp

    def test_to_timestamp(self):
        """Format should match YYYY-MM-DD_HH:MM:SS."""
        timestamp = DWT.to_timestamp(self.datetime)
        assert timestamp == "2025-02-01_12:30:15"

    # Chunk metadata

    def test_chunk_metadata__to_blob_name(self):
        """Can successfully convert a chunk's metadata into a blob name."""
        blob_name = DWT.ChunkMetadata(
            bq_table_name=self.bq_table_name,
            timestamp=self.timestamp,
            obj_i_start=self.obj_i_start,
            obj_i_end=self.obj_i_end,
            obj_count_digits=self.obj_count_digits,
        ).to_blob_name()
        assert blob_name == self.blob_name

    def test_chunk_metadata__from_blob_name(self):
        """Can successfully convert a chunk's metadata into a blob name."""
        chunk_metadata = DWT.ChunkMetadata.from_blob_name(self.blob_name)
        assert chunk_metadata.bq_table_name == self.bq_table_name
        assert chunk_metadata.timestamp == self.timestamp
        assert chunk_metadata.obj_i_start == self.obj_i_start
        assert chunk_metadata.obj_i_end == self.obj_i_end
        assert chunk_metadata.obj_count_digits == self.obj_count_digits

    # Init CSV writer

    def test_init_csv_writer(self):
        """
        Initializing a CSV writer returns the content stream and writer. The
        fields should be pre-written as headers and the writer should write to
        the buffer.
        """
        task = append_users
        csv_content, csv_writer = task.init_csv_writer()

        csv_row = ["a", "b", "c"]
        csv_writer.writerow(csv_row)

        assert csv_content.getvalue().strip() == "\n".join(
            [",".join(task.settings.fields), ",".join(csv_row)]
        )

    # Write CSV row

    def _test_write_csv_row(self, *values: t.Tuple[t.Any, str]):
        original_values = tuple(value[0] for value in values)
        formatted_values = [value[1] for value in values]

        csv_content, csv_writer = append_users.init_csv_writer()
        DWT.write_csv_row(csv_writer, original_values)

        assert csv_content.getvalue().strip().split("\n", maxsplit=1)[
            1
        ] == ",".join(formatted_values)

    def test_write_csv_row__bool(self):
        """Booleans are converted to 0 or 1."""
        self._test_write_csv_row((True, "1"), (False, "0"))

    def test_write_csv_row__datetime(self):
        """Datetimes are converted to ISO 8601 format with a space separator."""
        tz_aware_dt = self.datetime.replace(tzinfo=timezone(timedelta(hours=1)))
        self._test_write_csv_row((tz_aware_dt, "2025-02-01 11:30:15"))

    def test_write_csv_row__date(self):
        """Dates are converted to ISO 8601 format."""
        self._test_write_csv_row((self.date, "2025-02-01"))

    def test_write_csv_row__time(self):
        """Times are converted to ISO 8601 format, ignoring timezone info."""
        self._test_write_csv_row((self.time, "12:30:15"))

    def test_write_csv_row__str(self):
        """
        Strings containing commas and/or double quotes are correctly escaped.
        """
        self._test_write_csv_row(
            ("a", "a"), ("b,c", '"b,c"'), ('"d","e"', '"""d"",""e"""')
        )

    # Task

    # pylint: disable-next=too-many-arguments,too-many-locals
    def _test_task(
        self,
        task: DWT,
        retries: int = 0,
        since_previous_run: t.Optional[timedelta] = None,
        task_args: t.Optional[Args] = None,
        task_kwargs: t.Optional[KwArgs] = None,
    ):
        """Assert that a data warehouse task uploads chunks of data as CSVs.

        Args:
            task: The task to make assertions on.
            retries: How many times the task has been retried.
            since_previous_run: How long ago since the task was previously run.
            task_args: The arguments passed to the task.
            task_kwargs: The keyword arguments passed to the task.
        """

        # Validate args.
        assert 0 <= retries <= task.settings.max_retries

        # Get the queryset and order it if not already ordered.
        task_args, task_kwargs = task_args or tuple(), task_kwargs or {}
        queryset = task.get_queryset(*task_args, **task_kwargs)
        if not queryset.ordered:
            queryset = queryset.order_by("id")

        # Count the objects in the queryset.
        obj_count = queryset.count()
        # Assume we've uploaded 1 chunk if retrying.
        uploaded_obj_count = task.settings.chunk_size if retries else 0
        assert uploaded_obj_count <= obj_count
        assert (obj_count - uploaded_obj_count) > 0

        # Get the object count's current magnitude (number of digits) and
        # simulate a higher order of magnitude during the previous run.
        obj_count_digits = len(str(obj_count))
        uploaded_obj_count_digits = obj_count_digits + 1

        # Get the current datetime.
        now = datetime.now(timezone.utc)

        # If not the first run, generate blobs for the last timestamp.
        # Assume the same object count and timedelta.
        uploaded_blobs_from_last_timestamp = (
            MockGcsBlob.generate_list(
                task=task,
                timestamp=DWT.to_timestamp(now - since_previous_run),
                obj_i_start=1,
                obj_i_end=obj_count,
                obj_count_digits=obj_count_digits,
            )
            if since_previous_run is not None
            else []
        )

        # Generate blobs for the current timestamp.
        timestamp = DWT.to_timestamp(now)
        uploaded_blobs_from_current_timestamp = MockGcsBlob.generate_list(
            task=task,
            timestamp=timestamp,
            obj_i_start=1,
            obj_i_end=uploaded_obj_count,
            obj_count_digits=uploaded_obj_count_digits,
        )
        non_uploaded_blobs_from_current_timestamp = MockGcsBlob.generate_list(
            task=task,
            timestamp=timestamp,
            obj_i_start=uploaded_obj_count + 1,
            obj_i_end=obj_count,
            obj_count_digits=obj_count_digits,
        )

        # Generate a mock GCS bucket.
        bucket = MockGcsBucket(
            # Return the appropriate list based on the filters.
            list_blobs_return=(
                uploaded_blobs_from_current_timestamp
                if task.settings.only_list_blobs_from_current_timestamp
                else uploaded_blobs_from_last_timestamp
                + uploaded_blobs_from_current_timestamp
            ),
            # Return the blobs not yet uploaded in the current timestamp.
            new_blobs=non_uploaded_blobs_from_current_timestamp,
        )

        # Patch methods called in the task to create predetermined results.
        with patch.object(
            DWT, "_get_gcs_bucket", return_value=bucket
        ) as get_gcs_bucket:
            with patch("codeforlife.tasks.data_warehouse.datetime") as dt:
                dt_now = t.cast(MagicMock, dt.now)
                dt_now.return_value = now
                if retries:
                    task_kwargs[DWT.timestamp_key] = timestamp

                self.apply_task(
                    task.name,
                    task_args,
                    task_kwargs,
                    retries=retries,
                )

                if retries:
                    dt_now.assert_not_called()
                else:
                    dt_now.assert_called_once_with(timezone.utc)
            get_gcs_bucket.assert_called_once()

        # Assert that the blobs for the BigQuery table were listed. If the
        # table's write-mode is append, assert only the blobs in the current
        # timestamp were listed.
        bucket.list_blobs.assert_called_once_with(
            prefix=f"{task.settings.bq_table_name}/"
            + (
                timestamp
                if task.settings.only_list_blobs_from_current_timestamp
                else ""
            )
        )

        # Assert that all blobs not in the current timestamp were (not) deleted.
        for blob in uploaded_blobs_from_last_timestamp:
            if task.settings.delete_blobs_not_from_current_timestamp:
                blob.delete.assert_called_once()
            else:
                blob.delete.assert_not_called()

        # Assert that a blob was created for each non-uploaded blob.
        bucket.blob.assert_has_calls(
            [
                call(blob.name)
                for blob in non_uploaded_blobs_from_current_timestamp
            ]
        )

        # Assert that the uploaded blobs in the current timestamp were copied
        # with the magnitude corrected in their name and the old blobs deleted.
        for blob in uploaded_blobs_from_current_timestamp:
            blob.chunk_metadata.obj_count_digits = obj_count_digits
            blob.delete.assert_called_once()
        bucket.copy_blob.assert_has_calls(
            [
                call(
                    blob=blob,
                    destination_bucket=bucket,
                    new_name=blob.chunk_metadata.to_blob_name(),
                )
                for blob in uploaded_blobs_from_current_timestamp
            ]
        )

        # Assert that each blob was uploaded from a CSV string.
        for blob in non_uploaded_blobs_from_current_timestamp:
            csv_content, csv_writer = task.init_csv_writer()
            for values in t.cast(
                t.List[t.Tuple[t.Any, ...]],
                queryset.values_list(*task.settings.fields)[
                    blob.chunk_metadata.obj_i_start
                    - 1 : blob.chunk_metadata.obj_i_end
                ],
            ):
                DWT.write_csv_row(csv_writer, values)

            blob.upload_from_string.assert_called_once_with(
                csv_content.getvalue().strip(), content_type="text/csv"
            )

    def test_task__append__no_retry__no_previous_blobs(self):
        """
        1. All blobs are uploaded on the first run - no retries are required.
        2. Blobs from the previous timestamp are not in the bucket.
        """
        self._test_task(append_users)

    def test_task__append__no_retry__previous_blobs(self):
        """
        1. All blobs are uploaded on the first run - no retries are required.
        2. Blobs from the previous timestamp are in the bucket.
        3. The blobs from the previous timestamp are not deleted.
        """
        self._test_task(append_users, since_previous_run=timedelta(days=1))

    def test_task__append__retry__no_previous_blobs(self):
        """
        1. Some blobs are uploaded on the first run - retries are required.
        2. The order of magnitude in the object count has changed - the blobs
            uploaded in the previous run(s) need to be renamed.
        """
        self._test_task(append_users, retries=1)

    def test_task__overwrite__no_retry__previous_blobs(self):
        """
        1. All blobs are uploaded on the first run - no retries are required.
        2. Blobs from the previous timestamp are in the bucket.
        3. The blobs from the previous timestamp are deleted.
        """
        self._test_task(overwrite_users, since_previous_run=timedelta(days=1))
