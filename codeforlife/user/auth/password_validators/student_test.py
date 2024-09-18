"""
© Ocado Group
Created on 30/01/2024 at 12:36:00(+00:00).
"""

from ....tests import TestCase
from ...models import User
from .student import StudentPasswordValidator


# pylint: disable-next=missing-class-docstring
class TestStudentPasswordValidator(TestCase):
    def setUp(self):
        # TODO: Remove second check once we switch to new models
        self.user = User.objects.filter(
            new_student__isnull=False, new_student__class_field__isnull=False
        ).first()
        assert self.user is not None

        self.validator = StudentPasswordValidator()

    def test_validate__password_too_short(self):
        """Password cannot be too short"""
        password = "fxwSn"

        with self.assert_raises_validation_error("password_too_short"):
            self.validator.validate(password, self.user)
