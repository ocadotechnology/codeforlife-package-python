from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from ...models import User


class TestUser(TestCase):
    """Tests the User model."""

    fixtures = [
        "users.json",
        "teachers.json",
    ]

    def setUp(self):
        self.john_doe = User.objects.get(pk=1)
        self.jane_doe = User.objects.get(pk=2)

    def test_delete(self):
        now = timezone.now()
        with patch.object(timezone, "now", return_value=now) as timezone_now:
            self.john_doe.delete()

            assert timezone_now.call_count == 2
            assert self.john_doe.delete_after == now + User.delete_wait
            assert self.john_doe.last_saved_at == now

    def test_objects__delete(self):
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
        now = timezone.now()
        with patch.object(timezone, "now", return_value=now) as timezone_now:
            user = User.objects.create(
                first_name="first_name",
                last_name="last_name",
                email="example@email.com",
            )

            assert timezone_now.call_count == 1
            assert user.last_saved_at == now
