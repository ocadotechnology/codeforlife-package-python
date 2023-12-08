"""
© Ocado Group
Created on 08/12/2023 at 17:43:11(+00:00).
"""

from ....tests import ModelTestCase
from ...models import Teacher


class TestTeacher(ModelTestCase[Teacher]):
    """Tests the Teacher model."""

    def test_objects__create_user(self):
        """
        Create a user with a teacher profile.
        """

        teacher_fields = {"is_admin": True}
        user_fields = {
            "first_name": "first_name",
            "email": "example@codeforlife.com",
            "password": "password",
        }

        user = Teacher.objects.create_user(
            teacher=teacher_fields,
            **user_fields,
        )

        assert user.first_name == user_fields["first_name"]
        assert user.email == user_fields["email"]
        assert user.password != user_fields["password"]
        assert user.check_password(user_fields["password"])
        assert user.teacher.is_admin == teacher_fields["is_admin"]

    def test_students(self):
        """
        Get all students from all classes.
        """

        raise NotImplementedError()  # TODO
