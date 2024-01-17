"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from django.contrib.auth.models import AnonymousUser

from ....tests import PermissionTestCase
from ...models import School, User
from ...permissions import InSchool


# pylint: disable-next=missing-class-docstring,too-many-instance-attributes
class TestInSchool(PermissionTestCase[InSchool]):
    fixtures = [
        "users",
        "teachers",
        "schools",
        "classes",
        "students",
    ]

    def setUp(self):
        super().setUp()

        self.school_teacher_user = User.objects.get(pk=1)
        assert (
            self.school_teacher_user.teacher
            and self.school_teacher_user.teacher.school
        )
        self.school_teacher__school = self.school_teacher_user.teacher.school
        self.school_teacher_request = self.request_factory.get("/")
        self.school_teacher_request.user = self.school_teacher_user

        self.student_user = User.objects.get(pk=3)
        assert self.student_user.student
        self.student__school = self.student_user.student.school
        self.student_request = self.request_factory.get("/")
        self.student_request.user = self.student_user

        self.indy_user = User.objects.get(pk=5)
        assert not self.indy_user.teacher and not self.indy_user.student
        self.indy_request = self.request_factory.get("/")
        self.indy_request.user = self.indy_user

        self.non_school_teacher_user = User.objects.get(pk=6)
        assert (
            self.non_school_teacher_user.teacher
            and not self.non_school_teacher_user.teacher.school
        )
        self.non_school_teacher_request = self.request_factory.get("/")
        self.non_school_teacher_request.user = self.non_school_teacher_user

        self.anon_request = self.request_factory.get("/")
        self.anon_request.user = AnonymousUser()

    # pylint: disable-next=pointless-string-statement
    """
    Naming convention:
        test_{school_id}__{user_type}

    school_id: The id of a school. Options:
        - in_any_school: The user is in any school.
        - not_in_any_school: The user is not in any school.
        - in_school: A specific school the user is in.
        - not_in_school: A specific school the user is not in.

    user_type: The type of user. Options:
        - non_school_teacher: A teacher not in a school.
        - school_teacher: A teacher in a school.
        - student: A student.
        - indy: An independent.
        - anon: An anonymous user.
    """

    def test_in_any_school__school_teacher(self):
        """
        Teacher with a school is in any school.
        """

        self.assert_has_permission(
            self.school_teacher_request,
            init_kwargs={
                "school_id": None,
            },
        )

    def test_in_any_school__student(self):
        """
        Student is in any school.
        """

        self.assert_has_permission(
            self.student_request,
            init_kwargs={
                "school_id": None,
            },
        )

    def test_not_in_any_school__non_school_teacher(self):
        """
        Teacher without a school is not in any school.
        """

        self.assert_not_has_permission(
            self.non_school_teacher_request,
            init_kwargs={
                "school_id": None,
            },
        )

    def test_not_in_any_school__indy(self):
        """
        Independent is not in any school.
        """

        self.assert_not_has_permission(
            self.indy_request,
            init_kwargs={
                "school_id": None,
            },
        )

    def test_not_in_any_school__anon(self):
        """
        Anonymous user is not in any school.
        """

        self.assert_not_has_permission(
            self.anon_request,
            init_kwargs={
                "school_id": None,
            },
        )

    def test_in_school__school_teacher(self):
        """
        Teacher with a school is in a specific school.
        """

        self.assert_has_permission(
            self.school_teacher_request,
            init_kwargs={
                "school_id": self.school_teacher__school.id,
            },
        )

    def test_in_school__student(self):
        """
        Student is in a specific school.
        """

        self.assert_has_permission(
            self.student_request,
            init_kwargs={
                "school_id": self.student__school.id,
            },
        )

    def test_not_in_school__non_school_teacher(self):
        """
        Teacher without a school is not in a specific school.
        """

        school = School.objects.first()
        assert school is not None

        self.assert_not_has_permission(
            self.non_school_teacher_request,
            init_kwargs={
                "school_id": school.id,
            },
        )

    def test_not_in_school__school_teacher(self):
        """
        Teacher with a school is not in a specific school.
        """

        school = School.objects.exclude(
            id=self.school_teacher__school.id
        ).first()
        assert school is not None

        self.assert_not_has_permission(
            self.school_teacher_request,
            init_kwargs={
                "school_id": school.id,
            },
        )

    def test_not_in_school__student(self):
        """
        Student is not in a specific school.
        """

        school = School.objects.exclude(id=self.student__school.id).first()
        assert school is not None

        self.assert_not_has_permission(
            self.student_request,
            init_kwargs={
                "school_id": school.id,
            },
        )

    def test_not_in_school__indy(self):
        """
        Independent is not in a specific school.
        """

        school = School.objects.first()
        assert school is not None

        self.assert_not_has_permission(
            self.indy_request,
            init_kwargs={
                "school_id": school.id,
            },
        )

    def test_not_in_school__anon(self):
        """
        Anonymous user is not in a specific school.
        """

        school = School.objects.first()
        assert school is not None

        self.assert_not_has_permission(
            self.anon_request,
            init_kwargs={
                "school_id": school.id,
            },
        )
