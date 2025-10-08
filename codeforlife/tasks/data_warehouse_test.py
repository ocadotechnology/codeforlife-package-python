"""
© Ocado Group
Created on 02/10/2025 at 17:22:38(+01:00).
"""

import typing as t
from datetime import datetime, timedelta
from unittest.mock import MagicMock, call, patch

from celery import Celery
from django.utils import timezone

from ..tests import CeleryTestCase
from ..types import Args, KwArgs
from ..user.models import User
from .data_warehouse import DataWarehouseTask as DWT

# pylint: disable=missing-class-docstring


@DWT.shared(
    DWT.Options(
        bq_table_write_mode="append",
        chunk_size=10,
        fields=["first_name", "is_active"],
    )
)
def user__append():
    """Append all users in the "user__append" BigQuery table."""
    return User.objects.all()


@DWT.shared(
    DWT.Options(
        bq_table_write_mode="overwrite",
        chunk_size=10,
        fields=["first_name", "is_active"],
    )
)
def user__overwrite():
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
        dt_start_fstr: str,
        dt_end_fstr: str,
        obj_i_start: int,
        obj_i_end: int,
        obj_count_digits: int,
    ):
        """Generate a list of mock GCS blobs.

        Args:
            task: The task that produced these blobs.
            dt_start_fstr: The datetime span start as formatted string.
            dt_end_fstr: The datetime span end as formatted string.
            obj_i_start: The object index span start.
            obj_i_end: The object index span end.
            obj_count_digits: The number of digits in the object count

        Returns:
            A list of mock GCS blobs.
        """
        return [
            cls(
                chunk_metadata=DWT.ChunkMetadata(
                    bq_table_name=task.options.bq_table_name,
                    dt_start_fstr=dt_start_fstr,
                    dt_end_fstr=dt_end_fstr,
                    obj_i_start=obj_i_start,
                    obj_i_end=min(
                        obj_i_start + task.options.chunk_size - 1, obj_i_end
                    ),
                    obj_count_digits=obj_count_digits,
                )
            )
            for obj_i_start in range(
                obj_i_start, obj_i_end + 1, task.options.chunk_size
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


class TestDataWarehouseTask(CeleryTestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = Celery(broker="memory://")

        return super().setUpClass()

    def setUp(self):
        self.bq_table_name = "example"
        self.dt_start_fstr = DWT.ChunkMetadata.format_datetime(
            datetime(
                year=2025,
                month=1,
                day=1,
            )
        )
        self.dt_end_fstr = DWT.ChunkMetadata.format_datetime(
            datetime(
                year=2025,
                month=1,
                day=1,
            )
        )
        self.obj_i_start = 1
        self.obj_i_end = 100
        self.obj_count_digits = 4

        obj_i_start_fstr = str(self.obj_i_start).zfill(self.obj_count_digits)
        obj_i_end_fstr = str(self.obj_i_end).zfill(self.obj_count_digits)

        self.blob_name = (
            f"{self.bq_table_name}/"
            f"{self.dt_start_fstr}_{self.dt_end_fstr}"
            "__"
            f"{obj_i_start_fstr}_{obj_i_end_fstr}"
            ".csv"
        )

        return super().setUp()

    # Options

    def _test_options(
        self,
        code: str,
        bq_table_write_mode: DWT.Options.BqTableWriteMode = ("append"),
        chunk_size: int = 10,
        fields: t.Optional[t.List[str]] = None,
        **kwargs,
    ):
        with self.assert_raises_validation_error(code=code):
            DWT.Options(
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

    # Chunk metadata

    def test_chunk_metadata__format_datetime(self):
        """
        Dates are formatted as YYYY-MM-DD, time as HH:MM:SS, and joined with T.
        """
        formatted_dt = DWT.ChunkMetadata.format_datetime(
            datetime(year=2025, month=2, day=1, hour=12, minute=30, second=15)
        )
        assert formatted_dt == "2025-02-01T12:30:15"

    def test_chunk_metadata__to_blob_name(self):
        """Can successfully convert a chunk's metadata into a blob name."""
        blob_name = DWT.ChunkMetadata(
            bq_table_name=self.bq_table_name,
            dt_start_fstr=self.dt_start_fstr,
            dt_end_fstr=self.dt_end_fstr,
            obj_i_start=self.obj_i_start,
            obj_i_end=self.obj_i_end,
            obj_count_digits=self.obj_count_digits,
        ).to_blob_name()
        assert blob_name == self.blob_name

    def test_chunk_metadata__from_blob_name(self):
        """Can successfully convert a chunk's metadata into a blob name."""
        chunk_metadata = DWT.ChunkMetadata.from_blob_name(self.blob_name)
        assert chunk_metadata.bq_table_name == self.bq_table_name
        assert chunk_metadata.dt_start_fstr == self.dt_start_fstr
        assert chunk_metadata.dt_end_fstr == self.dt_end_fstr
        assert chunk_metadata.obj_i_start == self.obj_i_start
        assert chunk_metadata.obj_i_end == self.obj_i_end
        assert chunk_metadata.obj_count_digits == self.obj_count_digits

    # Format values

    def _test_format_values(self, *values: t.Tuple[t.Any, str]):
        original_values = tuple(value[0] for value in values)
        formatted_values = [value[1] for value in values]

        csv = DWT.format_values(original_values)
        assert csv.startswith("\n")
        assert csv.removeprefix("\n").split(",") == formatted_values

    def test_format_values__bool(self):
        """Booleans are converted to 0 or 1."""
        self._test_format_values((True, "1"), (False, "0"))

    # Task

    # pylint: disable-next=too-many-arguments,too-many-locals
    def _test_task(
        self,
        task: DWT,
        uploaded_chunk_count: int = 0,
        retry_obj_count: t.Optional[int] = None,
        now: t.Optional[datetime] = None,
        last_ran_at: t.Optional[timedelta] = None,
        task_args: t.Optional[Args] = None,
        task_kwargs: t.Optional[KwArgs] = None,
    ):
        """Assert that a data warehouse tasks uploads chunks of data as CSVs.

        Args:
            task: The task to make assertions on.
            uploaded_chunk_count: How many chunks have already been uploaded.
            retry_obj_count: The new object count when retrying.
            now: When the task is triggered.
            last_ran_at: How long ago the task was last successfully ran.
            task_args: The arguments passed to the task.
            task_kwargs: The keyword arguments passed to the task.
        """

        # Validate args.
        assert uploaded_chunk_count >= 0

        # Get the queryset and order it if not already ordered.
        task_args, task_kwargs = task_args or tuple(), task_kwargs or {}
        queryset = task.get_queryset(*task_args, **task_kwargs)
        if not queryset.ordered:
            queryset = queryset.order_by("id")

        # Count the objects in the queryset and get the count's magnitude.
        uploaded_obj_count = uploaded_chunk_count * task.options.chunk_size
        obj_count = queryset.count()
        assert uploaded_obj_count <= obj_count
        assert (obj_count - uploaded_obj_count) > 0
        obj_count_digits = len(str(obj_count))

        # Get the current datetime span.
        dt_end = timezone.make_aware(now or datetime.now())
        dt_start = dt_end if last_ran_at is None else dt_end - last_ran_at

        # If not the first run, generate blobs for the last datetime span.
        # Assume the same object count and timedelta.
        uploaded_blobs_from_last_dt_span: t.List[MockGcsBlob] = []
        if last_ran_at is not None:
            dt_start_fstr = DWT.ChunkMetadata.format_datetime(
                dt_start - last_ran_at
            )
            dt_end_fstr = DWT.ChunkMetadata.format_datetime(dt_start)
            uploaded_blobs_from_last_dt_span += MockGcsBlob.generate_list(
                task=task,
                dt_start_fstr=dt_start_fstr,
                dt_end_fstr=dt_end_fstr,
                obj_i_start=1,
                obj_i_end=obj_count,
                obj_count_digits=obj_count_digits,
            )

        # Generate blobs for the current datetime span.
        dt_start_fstr = DWT.ChunkMetadata.format_datetime(dt_start)
        dt_end_fstr = DWT.ChunkMetadata.format_datetime(dt_end)
        uploaded_blobs_from_current_dt_span = MockGcsBlob.generate_list(
            task=task,
            dt_start_fstr=dt_start_fstr,
            dt_end_fstr=dt_end_fstr,
            obj_i_start=1,
            obj_i_end=uploaded_obj_count,
            obj_count_digits=obj_count_digits,
        )
        non_uploaded_blobs_from_current_dt_span = MockGcsBlob.generate_list(
            task=task,
            dt_start_fstr=dt_start_fstr,
            dt_end_fstr=dt_end_fstr,
            obj_i_start=uploaded_obj_count + 1,
            obj_i_end=obj_count,
            obj_count_digits=obj_count_digits,
        )

        # Generate a mock GCS bucket.
        bucket = MockGcsBucket(
            # Return the appropriate list based on the filters.
            list_blobs_return=(
                uploaded_blobs_from_current_dt_span
                if task.options.only_list_blobs_in_current_dt_span
                else uploaded_blobs_from_last_dt_span
                + uploaded_blobs_from_current_dt_span
            ),
            # Return the blobs not yet uploaded in the current datetime span.
            new_blobs=non_uploaded_blobs_from_current_dt_span,
        )

        # Patch methods called in the task to create predetermined results.
        with patch.object(
            DWT, "_get_gcs_bucket", return_value=bucket
        ) as get_gcs_bucket:
            with patch.object(timezone, "now", return_value=now) as now_mock:
                self.apply_task(task.name, task_args, task_kwargs)

                now_mock.assert_called_once()
            get_gcs_bucket.assert_called_once()

        # Assert that the blobs for the BigQuery table were listed. If the
        # table's write-mode is append, assert only the blobs in the current
        # datetime span were listed.
        bucket.list_blobs.assert_called_once_with(
            prefix=f"{task.options.bq_table_name}/"
            + (
                dt_start_fstr
                if task.options.only_list_blobs_in_current_dt_span
                else ""
            )
        )

        # Assert that all blobs not in the current datetime span were (not)
        # deleted.
        for blob in uploaded_blobs_from_last_dt_span:
            if task.options.delete_blobs_not_in_current_dt_span:
                blob.delete.assert_called_once()
            else:
                blob.delete.assert_not_called()
        # bucket_copy_blob.assert_has_calls([])  # TODO

        # Assert that a blob was created for each non-uploaded blob.
        bucket.blob.assert_has_calls(
            [
                call(blob.name)
                for blob in non_uploaded_blobs_from_current_dt_span
            ]
        )

        # Assert that each blob was uploaded from a CSV string.
        for blob in non_uploaded_blobs_from_current_dt_span:
            csv = task.options.csv_headers
            for values in t.cast(
                t.List[t.Tuple[t.Any, ...]],
                queryset.values_list(*task.options.fields)[
                    blob.chunk_metadata.obj_i_start
                    - 1 : blob.chunk_metadata.obj_i_end
                ],
            ):
                csv += DWT.format_values(values)

            blob.upload_from_string.assert_called_once_with(
                csv, content_type="text/csv"
            )

    def test_task__append__first__no_retry(self):
        """
        1. This is the first datetime span.
        2. All blobs are uploaded on the first run - no retries are required.
        """
        self._test_task(task=user__append)

    def test_task__append__not_first__no_retry(self):
        """
        1. This is not the first datetime span.
        2. All blobs are uploaded on the first run - no retries are required.
        3. The blobs from the previous datetime span(s) are not deleted.
        """
        self._test_task(
            task=user__append,
            last_ran_at=timedelta(days=1),  # Last successful run was 1 day ago.
        )

    def test_task__append__first__retry(self):
        """
        1. This is the first datetime span.
        2. Some blobs are uploaded on the first run - retries are required.
        3. The order of magnitude in the object count has changed - the blobs
            blobs uploaded in the previous runs need to be renamed.
        """
        self._test_task(
            task=user__append,
            uploaded_chunk_count=1,  # Assume we've already uploaded 1 chunk.
        )

    def test_task__overwrite__not_first__no_retry(self):
        """
        1. This is the first datetime span.
        2. All blobs are uploaded on the first run - no retries are required.
        3. The blobs from the previous datetime span(s) are deleted.
        """
        self._test_task(
            task=user__overwrite,
            last_ran_at=timedelta(days=1),  # Last successful run was 1 day ago.
        )
