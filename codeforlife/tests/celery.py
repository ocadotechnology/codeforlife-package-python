"""
© Ocado Group
Created on 01/04/2025 at 16:57:19(+01:00).
"""

import typing as t
from datetime import datetime
from importlib import import_module
from unittest.mock import MagicMock, call, patch

from celery import Celery, Task
from django.utils import timezone

from ..tasks import DataWarehouseTask, get_task_name
from ..types import Args, KwArgs
from .test import TestCase


class CeleryTestCase(TestCase):
    """A test case for celery tasks."""

    _Chunk = DataWarehouseTask.ChunkMetadata  # shorthand

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

    class _MockGcsBlob(t.NamedTuple):
        chunk_metadata: DataWarehouseTask.ChunkMetadata
        upload_from_string: MagicMock
        delete: MagicMock

        @property
        def name(self):
            """The name of the blob."""
            return self.chunk_metadata.to_blob_name()

    class _MockGcsBucket(t.NamedTuple):
        list_blobs: MagicMock
        blob: MagicMock
        copy_blob: MagicMock

    def _generate_mock_gcs_blobs(
        self,
        task: DataWarehouseTask,
        dt_start_fstr: str,
        dt_end_fstr: str,
        obj_i_start: int,
        obj_count: int,
        obj_count_digits: int,
    ):
        return [
            self._MockGcsBlob(
                chunk_metadata=self._Chunk(
                    bq_table_name=task.options.bq_table_name,
                    dt_start_fstr=dt_start_fstr,
                    dt_end_fstr=dt_end_fstr,
                    obj_i_start=obj_i_start,
                    obj_i_end=min(
                        obj_i_start + task.options.chunk_size - 1, obj_count
                    ),
                    obj_count_digits=obj_count_digits,
                ),
                upload_from_string=MagicMock(),
                delete=MagicMock(),
            )
            for obj_i_start in range(
                obj_i_start, obj_count + 1, task.options.chunk_size
            )
        ]

    def assert_data_warehouse_task(
        self,
        task: DataWarehouseTask,
        uploaded_obj_count: int = 0,
        now: t.Optional[datetime] = None,
        last_ran_at: t.Optional[datetime] = None,
        task_args: t.Optional[Args] = None,
        task_kwargs: t.Optional[KwArgs] = None,
    ):
        # Set default values.
        now = timezone.make_aware(now or datetime.now())
        last_ran_at = timezone.make_aware(last_ran_at) if last_ran_at else now
        task_args, task_kwargs = task_args or tuple(), task_kwargs or {}

        # Get the queryset and order if not already ordered.
        query_set = task.get_query_set(*task_args, **task_kwargs)
        if not query_set.ordered:
            query_set = query_set.order_by("id")

        # Count the objects in the queryset and get the count's magnitude.
        obj_count = query_set.count()
        assert uploaded_obj_count <= obj_count, "Uploaded object count too high"
        obj_count_digits = len(str(obj_count))

        # Get formatted strings for the current datetime span's start and end.
        dt_start_fstr = self._Chunk.format_datetime(last_ran_at)
        dt_end_fstr = self._Chunk.format_datetime(now)

        # Generate mocks for all the uploaded and non-uploaded blobs.
        uploaded_blobs = self._generate_mock_gcs_blobs(
            task=task,
            dt_start_fstr=dt_start_fstr,
            dt_end_fstr=dt_end_fstr,
            obj_i_start=1,
            obj_count=uploaded_obj_count,
            obj_count_digits=obj_count_digits,
        )
        non_uploaded_blobs = self._generate_mock_gcs_blobs(
            task=task,
            dt_start_fstr=dt_start_fstr,
            dt_end_fstr=dt_end_fstr,
            obj_i_start=uploaded_obj_count + 1,
            obj_count=obj_count,
            obj_count_digits=obj_count_digits,
        )

        # Generate mocks for the bucket's methods.
        bucket_list_blobs = MagicMock(return_value=uploaded_blobs)
        bucket_blob = MagicMock(side_effect=non_uploaded_blobs)
        bucket_copy_blob = MagicMock()

        # Patch methods called in the task to create predetermined results.
        with patch.object(
            DataWarehouseTask,
            "_get_gcs_bucket",
            return_value=self._MockGcsBucket(
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
            [call(blob.name) for blob in non_uploaded_blobs]
        )

        # Assert that each blob was uploaded from a CSV string.
        for blob in non_uploaded_blobs:
            csv = task.options.csv_headers
            for values in t.cast(
                t.List[t.Tuple[t.Any, ...]],
                query_set.values_list(*task.options.fields)[
                    blob.chunk_metadata.obj_i_start
                    - 1 : blob.chunk_metadata.obj_i_end
                ],
            ):
                csv += DataWarehouseTask.format_values(values)

            t.cast(MagicMock, blob.upload_from_string).assert_called_once_with(
                csv, content_type="text/csv"
            )

        # bucket_copy_blob.assert_has_calls([])  # TODO
