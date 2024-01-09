"""
© Ocado Group
Created on 08/12/2023 at 17:37:30(+00:00).
"""

from ....tests import ModelTestCase
from ...models import Class, School, Student, Teacher, User


class TestUser(ModelTestCase[User]):
    """Tests the User model."""

    fixtures = [
        "users",
        "teachers",
        "schools",
        "classes",
        "students",
    ]

    def setUp(self):
        self.klass__AB123 = Class.objects.get(pk="AB123")
        self.school__1 = School.objects.get(pk=1)
        self.student__1 = Student.objects.get(pk=1)

    # TODO: test docstrings.

    def test_save__create(self):
        """
        Cannot create a user calling save.
        """

        with self.assert_raises_integrity_error():
            User(
                first_name="first_name",
                last_name="last_name",
                email="example@codeforlife.com",
                password="password",
            ).save()

    def test_save__first_name__student(self):
        """
        Students must have a unique name per class.
        """

        student = Student.objects.create(
            auto_gen_password="password",
            klass=self.student__1.klass,
            school=self.student__1.school,
        )

        with self.assert_raises_integrity_error():
            User.objects.create_user(
                first_name=self.student__1.user.first_name,
                password="password",
                student=student,
            )

    def test_constraints__profile(self):
        """
        Cannot be a student and a teacher.
        """

        teacher = Teacher.objects.create()
        student = Student.objects.create(
            auto_gen_password="password",
            klass=self.klass__AB123,
            school=self.school__1,
        )

        with self.assert_raises_integrity_error():
            User.objects.create_user(
                password="password",
                first_name="student_and_teacher",
                last_name="last_name",
                student=student,
                teacher=teacher,
            )

    def test_constraints__email__teacher(self):
        """
        Teachers must have an email.
        """

        teacher = Teacher.objects.create()

        with self.assert_raises_integrity_error():
            User.objects.create_user(
                password="password",
                first_name="teacher",
                last_name="last_name",
                teacher=teacher,
            )

    def test_constraints__email__student(self):
        """
        Student cannot have an email.
        """

        student = Student.objects.create(
            auto_gen_password="password",
            klass=self.klass__AB123,
            school=self.school__1,
        )

        with self.assert_raises_integrity_error():
            User.objects.create_user(
                password="password",
                first_name="student",
                student=student,
                email="student@codeforlife.com",
            )

    def test_constraints__email__indy(self):
        """
        Independents must have an email.
        """

        with self.assert_raises_integrity_error():
            User.objects.create_user(
                password="password",
                first_name="first_name",
                last_name="last_name",
            )

    def test_constraints__last_name__teacher(self):
        """
        Teachers must have a last name.
        """

        teacher = Teacher.objects.create()

        with self.assert_raises_integrity_error():
            User.objects.create_user(
                password="password",
                first_name="teacher",
                email="teacher@codeforlife.com",
                teacher=teacher,
            )

    def test_constraints__last_name__students(self):
        """
        Students can't have a last name.
        """

        student = Student.objects.create(
            auto_gen_password="password",
            klass=self.klass__AB123,
            school=self.school__1,
        )

        with self.assert_raises_integrity_error():
            User.objects.create_user(
                password="password",
                first_name="student",
                last_name="last_name",
                student=student,
            )

    def test_constraints__last_name__indy(self):
        """
        Independents must have a last name.
        """

        with self.assert_raises_integrity_error():
            User.objects.create_user(
                password="password",
                first_name="Indiana",
                email="independent@codeforlife.com",
            )

    def test_constraints__is_staff(self):
        """
        Students cannot be a staff user.
        """

        with self.assert_raises_integrity_error():
            User.objects.create_user(
                first_name="Indiana",
                password="password",
                student=Student.objects.create(
                    auto_gen_password="password",
                    klass=self.klass__AB123,
                    school=self.school__1,
                ),
                is_staff=True,
            )

    def test_constraints__is_superuser(self):
        """
        Students cannot be a super user.
        """

        with self.assert_raises_integrity_error():
            User.objects.create_user(
                first_name="Indiana",
                password="password",
                student=Student.objects.create(
                    auto_gen_password="password",
                    klass=self.klass__AB123,
                    school=self.school__1,
                ),
                is_superuser=True,
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

        user_fields = {
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "example@codeforlife.com",
            "password": "password",
            "teacher": Teacher.objects.create(),
        }

        user = User.objects.create_user(**user_fields)  # type: ignore[arg-type]
        assert user.first_name == user_fields["first_name"]
        assert user.last_name == user_fields["last_name"]
        assert user.email == user_fields["email"]
        assert user.password != user_fields["password"]
        assert user.check_password(user_fields["password"])
        assert user.teacher == user_fields["teacher"]

    def test_objects__create_user__student(self):
        """
        Create a student user.
        """

        user_fields = {
            "first_name": "first_name",
            "password": "password",
            "student": Student.objects.create(
                auto_gen_password="password",
                klass=self.klass__AB123,
                school=self.school__1,
            ),
        }

        user = User.objects.create_user(**user_fields)  # type: ignore[arg-type]
        assert user.first_name == user_fields["first_name"]
        assert user.password != user_fields["password"]
        assert user.check_password(user_fields["password"])
        assert user.student == user_fields["student"]

    def test_objects__create_user__indy(self):
        """
        Create an independent user.
        """

        user_fields = {
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "example@codeforlife.com",
            "password": "password",
        }

        user = User.objects.create_user(**user_fields)
        assert user.first_name == user_fields["first_name"]
        assert user.last_name == user_fields["last_name"]
        assert user.email == user_fields["email"]
        assert user.password != user_fields["password"]
        assert user.check_password(user_fields["password"])

    def test_objects__create_superuser__teacher(self):
        """
        Create a teacher super user.
        """

        user_fields = {
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "example@codeforlife.com",
            "password": "password",
            "teacher": Teacher.objects.create(),
        }

        user = User.objects.create_superuser(
            **user_fields  # type: ignore[arg-type]
        )
        assert user.first_name == user_fields["first_name"]
        assert user.last_name == user_fields["last_name"]
        assert user.email == user_fields["email"]
        assert user.password != user_fields["password"]
        assert user.check_password(user_fields["password"])
        assert user.teacher == user_fields["teacher"]
        assert user.is_staff
        assert user.is_superuser

    def test_objects__create_superuser__indy(self):
        """
        Create an independent super user.
        """

        user_fields = {
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "example@codeforlife.com",
            "password": "password",
        }

        user = User.objects.create_superuser(**user_fields)
        assert user.first_name == user_fields["first_name"]
        assert user.last_name == user_fields["last_name"]
        assert user.email == user_fields["email"]
        assert user.password != user_fields["password"]
        assert user.check_password(user_fields["password"])
        assert user.is_staff
        assert user.is_superuser