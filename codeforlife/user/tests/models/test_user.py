"""
© Ocado Group
Created on 08/12/2023 at 17:37:30(+00:00).
"""

from ....tests import ModelTestCase
from ...models import Student, Teacher, User


class TestUser(ModelTestCase[User]):
    """Tests the User model."""

    def test_constraints__profile(self):
        """
        Independents must have an email.
        """

        with self.assert_raises_integrity_error():
            User.objects.create(
                first_name="student_and_teacher",
                teacher=Teacher.objects.create(),
                student=Student.objects.create(auto_gen_password="password"),
            )

    def test_constraints__email__teacher(self):
        """
        Teachers must have an email.
        """

        with self.assert_raises_integrity_error():
            User.objects.create(
                first_name="teacher",
                teacher=Teacher.objects.create(),
            )

    def test_constraints__email__student(self):
        """
        Student cannot have an email.
        """

        with self.assert_raises_integrity_error():
            User.objects.create(
                first_name="student",
                student=Student.objects.create(auto_gen_password="password"),
                email="student@codeforlife.com",
            )

    def test_constraints__email__indy(self):
        """
        Independents must have an email.
        """

        with self.assert_raises_integrity_error():
            User.objects.create(
                first_name="first_name",
            )

    def test_objects__create(self):
        """
        Cannot call objects.create.
        """

        with self.assert_raises_integrity_error():
            User.objects.create()

    def test_objects__create_user__teacher(self):
        """
        Create a teacher user.
        """

        raise NotImplementedError()  # TODO

    def test_objects__create_user__student(self):
        """
        Create a student user.
        """

        raise NotImplementedError()  # TODO

    def test_objects__create_user__indy(self):
        """
        Create an independent user.
        """

        user_fields = {
            "first_name": "first_name",
            "email": "example@codeforlife.com",
            "password": "password",
        }

        user = User.objects.create_user(**user_fields)
        assert user.first_name == user_fields["first_name"]
        assert user.email == user_fields["email"]
        assert user.password != user_fields["password"]
        assert user.check_password(user_fields["password"])

    def test_objects__create_superuser__teacher(self):
        """
        Create a teacher super user.
        """

        raise NotImplementedError()  # TODO

    def test_objects__create_superuser__student(self):
        """
        Create a student super user.
        """

        raise NotImplementedError()  # TODO

    def test_objects__create_superuser__indy(self):
        """
        Create an independent super user.
        """

        user_fields = {
            "first_name": "first_name",
            "email": "example@codeforlife.com",
            "password": "password",
        }

        user = User.objects.create_superuser(**user_fields)
        assert user.first_name == user_fields["first_name"]
        assert user.email == user_fields["email"]
        assert user.password != user_fields["password"]
        assert user.check_password(user_fields["password"])
        assert user.is_staff
        assert user.is_superuser
