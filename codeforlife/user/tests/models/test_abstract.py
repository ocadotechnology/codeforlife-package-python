"""
© Ocado Group
Created on 08/12/2023 at 15:48:38(+00:00).
"""

from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from ...models import User


class TestAbstract(TestCase):
    """
    Tests the abstract model inherited by other models.

    Abstract model path: codeforlife.models
    """

    fixtures = [
        "users",
        "teachers",
    ]

    def setUp(self):
        self.john_doe = User.objects.get(pk=1)
        self.jane_doe = User.objects.get(pk=2)

    def test_delete(self):
        """
        Deleting a model instance sets its deletion schedule.
        """

        now = timezone.now()
        with patch.object(timezone, "now", return_value=now) as timezone_now:
            self.john_doe.delete()

            assert timezone_now.call_count == 2
            assert self.john_doe.delete_after == now + User.delete_wait
            assert self.john_doe.last_saved_at == now

    def test_objects__delete(self):
        """
        Deleting a set of models in a query sets their deletion schedule.
        """

        now = timezone.now()
        with patch.object(timezone, "now", return_value=now) as timezone_now:
            User.objects.filter(
                pk__in=[
                    self.john_doe.pk,
                    self.jane_doe.pk,
                ]
            ).delete()

            assert timezone_now.call_count == 2

            self.john_doe.refresh_from_db()
            assert self.john_doe.delete_after == now + User.delete_wait
            assert self.john_doe.last_saved_at == now

            self.jane_doe.refresh_from_db()
            assert self.jane_doe.delete_after == now + User.delete_wait
            assert self.jane_doe.last_saved_at == now

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
