"""
© Ocado Group
Created on 30/01/2024 at 12:36:00(+00:00).
"""

from .base import PasswordValidatorTestCase
from ....auth.password_validators import StudentPasswordValidator
from ....models.user import User


class TestStudentPasswordValidator(PasswordValidatorTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.filter(new_student__isnull=False).first()
        assert cls.user is not None

        cls.validator = StudentPasswordValidator()
        super(TestStudentPasswordValidator, cls).setUpClass()

    def test_validate__password_too_short(self):
        """Check password validator rejects too short password"""
        password = "fxwSn"

        with self.assert_raises_validation_error("password_too_short"):
            self.validator.validate(password, self.user)
