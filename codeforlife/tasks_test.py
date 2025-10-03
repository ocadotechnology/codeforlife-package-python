"""
© Ocado Group
Created on 02/10/2025 at 17:22:38(+01:00).
"""

from unittest.mock import patch

from celery import Celery

from .tasks import save_query_set_as_csvs_in_gcs_bucket
from .tests import CeleryTestCase
from .user.models import User

# pylint: disable=missing-class-docstring


@save_query_set_as_csvs_in_gcs_bucket(
    bq_table_write_mode="append",
    chunk_size=500,
    fields=["first_name", "is_active"],
)
def users__append():
    """Append users to table"""
    return User.objects.all()


class TestSaveQuerySetAsCsvsInGcsBucket(CeleryTestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Celery(broker="memory://")

        return super().setUpClass()

    def test_users__append(self):
        self.apply_task("codeforlife.tasks_test.users__append")
