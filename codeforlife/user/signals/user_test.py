"""
© Ocado Group
Created on 14/03/2024 at 12:14:54(+00:00).
"""

from ...tests import TestCase
from ..models import User


class UserSignalsTests(TestCase):
    fixtures = ["school_1"]

    def setUp(self):
        user = User.objects.first()
        assert user
        self.user = user

    def test_pre_save__update_fields_incomplete__first_name(self):
        """
        Saving a User with only one of the first_name fields in update_fields
        should raise a ValidationError, but saving with both or neither should
        succeed.
        """

        with self.subTest("Only _first_name included in update_fields"):
            with self.assert_raises_validation_error(
                "update_fields_incomplete"
            ):
                self.user.save(update_fields={"_first_name"})

        with self.subTest("Only _first_name_hash included in update_fields"):
            with self.assert_raises_validation_error(
                "update_fields_incomplete"
            ):
                self.user.save(update_fields={"_first_name_hash"})

        with self.subTest(
            "Neither _first_name nor _first_name_hash included in update_fields"
        ):
            self.user.save()
            self.user.save(update_fields={})

        with self.subTest(
            "Both _first_name and _first_name_hash included in update_fields"
        ):
            self.user.first_name = "John"
            self.user.save(update_fields={"_first_name", "_first_name_hash"})

    def test_pre_save__update_fields_incomplete__email(self):
        """
        Saving a User with only one of the email fields in update_fields should
        raise a ValidationError, but saving with both or neither should succeed.
        """

        with self.subTest("Only _email included in update_fields"):
            with self.assert_raises_validation_error(
                "update_fields_incomplete"
            ):
                self.user.save(update_fields={"_email"})

        with self.subTest("Only _email_hash included in update_fields"):
            with self.assert_raises_validation_error(
                "update_fields_incomplete"
            ):
                self.user.save(update_fields={"_email_hash"})

        with self.subTest(
            "Neither _email nor _email_hash included in update_fields"
        ):
            self.user.save()
            self.user.save(update_fields={})

        with self.subTest(
            "Both _email and _email_hash included in update_fields"
        ):
            self.user.email = "john.doe@example.com"
            self.user.save(update_fields={"_email", "_email_hash"})
