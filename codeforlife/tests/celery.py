"""
© Ocado Group
Created on 01/04/2025 at 16:57:19(+01:00).
"""

import typing as t
from datetime import datetime, timedelta
from importlib import import_module
from unittest.mock import MagicMock, call, patch

from celery import Celery, Task
from django.utils import timezone

from ..tasks import DataWarehouseTask as DWT
from ..tasks import get_task_name
from ..types import Args, KwArgs
from .test import TestCase


class MockGcsBlob(t.NamedTuple):
    """A mocked blob in a GCS bucket."""

    chunk_metadata: DWT.ChunkMetadata
    upload_from_string: MagicMock
    delete: MagicMock

    @property
    def name(self):
        """The name of the blob."""
        return self.chunk_metadata.to_blob_name()

    def __repr__(self):
        return self.name


class MockGcsBucket(t.NamedTuple):
    """A mocked GCS bucket."""

    list_blobs: MagicMock
    blob: MagicMock
    copy_blob: MagicMock


class CeleryTestCase(TestCase):
    """A test case for celery tasks."""

    # The dot-path of the module containing the Celery app.
    app_module: str = "application"
    # The name of the Celery app.
    app_name: str = "celery"
    # The Celery app instance. Auto-imported if not set.
    app: Celery

    @classmethod
    def setUpClass(cls):
        if not hasattr(cls, "app"):
            cls.app = getattr(import_module(cls.app_module), cls.app_name)

        return super().setUpClass()

    def apply_task(
        self,
        name: str,
        args: t.Optional[Args] = None,
        kwargs: t.Optional[KwArgs] = None,
    ):
        """Apply a task.

        Args:
            name: The name of the task.
            args: The args to pass to the task.
            kwargs: The keyword args to pass to the task.
        """
        task: Task = self.app.tasks[get_task_name(name)]
        task.apply(args=args, kwargs=kwargs)

    # pylint: disable-next=too-many-arguments,too-many-locals
    def assert_data_warehouse_task(
        self,
        task: DWT,
        uploaded_chunk_count: int = 0,
        now: t.Optional[datetime] = None,
        last_ran_at: t.Optional[timedelta] = None,
        task_args: t.Optional[Args] = None,
        task_kwargs: t.Optional[KwArgs] = None,
    ):
        # pylint: disable=line-too-long
        """Assert that a data warehouse tasks uploads chunks of data as CSVs.

        Args:
            task: The task to make assertions on.
            uploaded_chunk_count: How many chunks have already been uploaded.
            now: When the task is triggered.
            last_ran_at: How long ago the task was last successfully ran.
            task_args: The arguments passed to the task.
            task_kwargs: The keyword arguments passed to the task.
        """
        # pylint: enable=line-too-long

        # Validate args.
        assert uploaded_chunk_count >= 0

        # Get the queryset and order it if not already ordered.
        task_args, task_kwargs = task_args or tuple(), task_kwargs or {}
        query_set = task.get_query_set(*task_args, **task_kwargs)
        if not query_set.ordered:
            query_set = query_set.order_by("id")

        # Count the objects in the queryset and get the count's magnitude.
        uploaded_obj_count = uploaded_chunk_count * task.options.chunk_size
        obj_count = query_set.count()
        assert uploaded_obj_count <= obj_count
        assert (obj_count - uploaded_obj_count) > 0
        obj_count_digits = len(str(obj_count))

        # Local utility to generate blob-mocks for selected spans.
        def generate_blobs(
            dt_start_fstr: str,
            dt_end_fstr: str,
            obj_i_start: int,
            obj_i_end: int,
        ):
            return [
                MockGcsBlob(
                    chunk_metadata=DWT.ChunkMetadata(
                        bq_table_name=task.options.bq_table_name,
                        dt_start_fstr=dt_start_fstr,
                        dt_end_fstr=dt_end_fstr,
                        obj_i_start=obj_i_start,
                        obj_i_end=min(
                            obj_i_start + task.options.chunk_size - 1, obj_i_end
                        ),
                        obj_count_digits=obj_count_digits,
                    ),
                    upload_from_string=MagicMock(),
                    delete=MagicMock(),
                )
                for obj_i_start in range(
                    obj_i_start, obj_i_end + 1, task.options.chunk_size
                )
            ]

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
            uploaded_blobs_from_last_dt_span += generate_blobs(
                dt_start_fstr, dt_end_fstr, 1, obj_count
            )

        # Generate blobs for the current datetime span.
        dt_start_fstr = DWT.ChunkMetadata.format_datetime(dt_start)
        dt_end_fstr = DWT.ChunkMetadata.format_datetime(dt_end)
        uploaded_blobs_from_current_dt_span = generate_blobs(
            dt_start_fstr, dt_end_fstr, 1, uploaded_obj_count
        )
        non_uploaded_blobs_from_current_dt_span = generate_blobs(
            dt_start_fstr, dt_end_fstr, uploaded_obj_count + 1, obj_count
        )

        # Generate mocks for the bucket's methods.
        bucket_list_blobs = MagicMock(
            return_value=(  # Return the appropriate list based on the filters.
                uploaded_blobs_from_current_dt_span
                if task.options.only_list_blobs_in_current_dt_span
                else uploaded_blobs_from_last_dt_span
                + uploaded_blobs_from_current_dt_span
            )
        )
        bucket_blob = MagicMock(
            # Return the blobs not yet uploaded in the current datetime span.
            side_effect=non_uploaded_blobs_from_current_dt_span  # 1 blob p/call
        )
        bucket_copy_blob = MagicMock()

        # Patch methods called in the task to create predetermined results.
        with patch.object(
            DWT,
            "_get_gcs_bucket",
            return_value=MockGcsBucket(
                list_blobs=bucket_list_blobs,
                blob=bucket_blob,
                copy_blob=bucket_copy_blob,
            ),
        ) as get_gcs_bucket:
            with patch.object(timezone, "now", return_value=now) as now_mock:
                self.apply_task(task.name, task_args, task_kwargs)

                now_mock.assert_called_once()
            get_gcs_bucket.assert_called_once()

        # Assert that the blobs for the BigQuery table were listed. If the
        # table's write-mode is append, assert only the blobs in the current
        # datetime span were listed.
        bucket_list_blobs.assert_called_once_with(
            prefix=f"{task.options.bq_table_name}/"
            + (
                dt_start_fstr
                if task.options.only_list_blobs_in_current_dt_span
                else ""
            )
        )

        # Assert that a blob was created for each non-uploaded blob.
        bucket_blob.assert_has_calls(
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
                query_set.values_list(*task.options.fields)[
                    blob.chunk_metadata.obj_i_start
                    - 1 : blob.chunk_metadata.obj_i_end
                ],
            ):
                csv += DWT.format_values(values)

            t.cast(MagicMock, blob.upload_from_string).assert_called_once_with(
                csv, content_type="text/csv"
            )

        # bucket_copy_blob.assert_has_calls([])  # TODO
