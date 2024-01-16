"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from django.contrib.auth.models import AnonymousUser

from ....tests import PermissionTestCase
from ...models import User
from ...permissions import IsStudent


# pylint: disable-next=missing-class-docstring
class TestIsStudent(PermissionTestCase[IsStudent]):
    fixtures = [
        "users",
        "teachers",
        "schools",
        "classes",
        "students",
    ]

    def setUp(self):
        super().setUp()

        self.user__1 = User.objects.get(pk=1)
        self.user__3 = User.objects.get(pk=3)
        self.user__4 = User.objects.get(pk=4)
        self.user__5 = User.objects.get(pk=5)

        assert self.user__1.teacher
        assert self.user__3.student
        assert self.user__4.student
        assert not self.user__5.student and not self.user__5.teacher

        self.user__1__teacher = self.user__1.teacher
        self.user__3__student = self.user__3.student
        self.user__4__student = self.user__4.student

        self.request__1 = self.request_factory.get("/")
        self.request__1.user = self.user__1
        self.request__3 = self.request_factory.get("/")
        self.request__3.user = self.user__3
        self.request__5 = self.request_factory.get("/")
        self.request__5.user = self.user__5

    # pylint: disable-next=pointless-string-statement
    """
    Naming convention:
        test_{user_type}__{student_id}

    user_type: The type of user. Options:
        - teacher: A teacher.
        - student: A student.
        - indy: An independent.
        - anon: An anonymous user.

    student_id: The ID of a student. Options:
        - any_student: User is any student.
        - not_any_student: User is not any student.
        - specific_student: User is a specific student.
        - not_specific_student User is not a specific student.
    """

    def test_teacher__not_any_student(self):
        """
        Teacher is not any student.
        """

        self.assert_not_has_permission(
            self.request__1,
            init_kwargs={
                "student_id": None,
            },
        )

    def test_indy__not_any_student(self):
        """
        Independent is not any student.
        """

        self.assert_not_has_permission(
            self.request__5,
            init_kwargs={
                "student_id": None,
            },
        )

    def test_anon__not_any_student(self):
        """
        Anonymous user is not any student.
        """

        request = self.request_factory.get("/")
        request.user = AnonymousUser()

        self.assert_not_has_permission(request)

    def test_student__any_student(self):
        """
        Student is any student.
        """

        self.assert_has_permission(
            self.request__3,
            init_kwargs={
                "student_id": None,
            },
        )

    def test_student__specific_student(self):
        """
        Student is a specific student.
        """

        self.assert_has_permission(
            self.request__3,
            init_kwargs={
                "student_id": self.user__3__student.id,
            },
        )

    def test_student__not_specific_student(self):
        """
        Student is not a specific student.
        """

        self.assert_not_has_permission(
            self.request__3,
            init_kwargs={
                "student_id": self.user__4__student.id,
            },
        )
