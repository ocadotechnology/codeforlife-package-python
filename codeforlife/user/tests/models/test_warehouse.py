"""
© Ocado Group
Created on 08/12/2023 at 15:48:38(+00:00).
"""

from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from ....tests import ModelTestCase
from ...models import User


class TestWarehouse(ModelTestCase[User]):
    """
    Tests the abstract model inherited by other models.

    Abstract model path: codeforlife.models
    """

    # TODO: group fixtures by scenarios, not model classes.
    fixtures = [
        "users",
        "teachers",
        "schools",
        "classes",
        "students",
    ]

    def setUp(self):
        self.user__1 = User.objects.get(pk=1)
        self.user__2 = User.objects.get(pk=2)

    # TODO: test docstrings.

    def test_delete__wait(self):
        """
        Set a model's deletion schedule.
        """

        now = timezone.now()
        with patch.object(timezone, "now", return_value=now) as timezone_now:
            self.user__1.delete()

            assert timezone_now.call_count == 2
            assert self.user__1.delete_after == now + User.delete_wait
            assert self.user__1.last_saved_at == now

    def test_delete__now(self):
        """
        Delete a model now.
        """

        self.user__1.delete(wait=timedelta())
        self.assert_does_not_exist(self.user__1)

    def test_objects__delete__wait(self):
        """
        Set many models deletion schedules.
        """

        now = timezone.now()
        with patch.object(timezone, "now", return_value=now) as timezone_now:
            User.objects.filter(
                pk__in=[
                    self.user__1.pk,
                    self.user__2.pk,
                ]
            ).delete()

            assert timezone_now.call_count == 2

            self.user__1.refresh_from_db()
            assert self.user__1.delete_after == now + User.delete_wait
            assert self.user__1.last_saved_at == now

            self.user__2.refresh_from_db()
            assert self.user__2.delete_after == now + User.delete_wait
            assert self.user__2.last_saved_at == now

    def test_objects__delete__now(self):
        """
        Delete many models now.
        """

        User.objects.filter(
            pk__in=[
                self.user__1.pk,
                self.user__2.pk,
            ]
        ).delete(wait=timedelta())

        self.assert_does_not_exist(self.user__1)
        self.assert_does_not_exist(self.user__2)

    def test_objects__create(self):
        """
        Creating a model records when it was first saved.
        """

        now = timezone.now()
        with patch.object(timezone, "now", return_value=now) as timezone_now:
            user = User.objects.create_user(
                password="password",
                first_name="first_name",
                last_name="last_name",
                email="example@email.com",
            )

            assert timezone_now.call_count == 1
            assert user.last_saved_at == now

    def test_objects__bulk_create(self):
        """
        Bulk creating models records when they were first saved.
        """

        now = timezone.now()
        with patch.object(timezone, "now", return_value=now) as timezone_now:
            users = User.objects.bulk_create(
                [
                    User(
                        first_name="first_name_1",
                        last_name="last_name_1",
                        email="example_1@email.com",
                    ),
                    User(
                        first_name="first_name_2",
                        last_name="last_name_2",
                        email="example_2@email.com",
                    ),
                ]
            )

            assert timezone_now.call_count == 2
            assert all(user.last_saved_at == now for user in users)
