"""
© Ocado Group
Created on 02/10/2025 at 17:22:38(+01:00).
"""

import typing as t
from datetime import datetime

from celery import Celery

from ..tests import CeleryTestCase
from ..user.models import User
from .data_warehouse import DataWarehouseTask

# pylint: disable=missing-class-docstring


@DataWarehouseTask.shared(
    DataWarehouseTask.Options(
        bq_table_write_mode="append",
        chunk_size=10,
        fields=["first_name", "is_active"],
    )
)
def user():
    """Append all users to the "user" BigQuery table."""
    return User.objects.all()


class TestDataWarehouseTask(CeleryTestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = Celery(broker="memory://")

        return super().setUpClass()

    # Options

    def _test_options(
        self,
        code: str,
        bq_table_write_mode: DataWarehouseTask.Options.BqTableWriteMode = (
            "append"
        ),
        chunk_size: int = 10,
        fields: t.Optional[t.List[str]] = None,
        **kwargs
    ):
        with self.assert_raises_validation_error(code=code):
            DataWarehouseTask.Options(
                bq_table_write_mode=bq_table_write_mode,
                chunk_size=chunk_size,
                fields=fields or ["some_field"],
                **kwargs
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
        """Base must be a subclass of DataWarehouseTask."""
        self._test_options(code="base_not_subclass", base=int)

    # Format values

    def _test_format_values(self, *values: t.Tuple[t.Any, str]):
        original_values = tuple(value[0] for value in values)
        formatted_values = [value[1] for value in values]

        csv = DataWarehouseTask.format_values(original_values)
        assert csv.startswith("\n")
        assert csv.removeprefix("\n").split(",") == formatted_values

    def test_format_values__bool(self):
        """Booleans are converted to 0 or 1."""
        self._test_format_values((True, "1"), (False, "0"))

    # Task

    def test_task__basic(self):
        """Everything completes on the 1st attempt without complications."""
        self.assert_data_warehouse_task(
            task=user, now=datetime(year=2025, month=1, day=1)
        )

    def test_task__overwrite(self):
        """
        Everything completes on the 1st attempt without complications. Any
        existing data is deleted.
        """

    def test_task__retry__basic(self):
        """
        The first attempt uploads only some of the CSVs. A second attempt is
        required to upload the remainder of the CSVs.
        """

    def test_task__retry__magnitude(self):
        """
        The first attempt uploads only some of the CSVs. A second attempt is
        required to upload the remainder of the CSVs. In addition, the number of
        objects has changed and therefore changed the order of magnitude.
        """
