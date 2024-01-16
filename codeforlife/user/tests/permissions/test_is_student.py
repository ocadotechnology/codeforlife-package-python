"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from django.contrib.auth.models import AnonymousUser

from ....tests import PermissionTestCase
from ...models import Student, User
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

        self.teacher_user = User.objects.get(pk=1)
        assert self.teacher_user.teacher
        self.teacher = self.teacher_user.teacher
        self.teacher_request = self.request_factory.get("/")
        self.teacher_request.user = self.teacher_user

        self.student_user = User.objects.get(pk=3)
        assert self.student_user.student
        self.student = self.student_user.student
        self.student_request = self.request_factory.get("/")
        self.student_request.user = self.student_user

        self.indy_user = User.objects.get(pk=5)
        assert not self.indy_user.student and not self.indy_user.teacher
        self.indy_request = self.request_factory.get("/")
        self.indy_request.user = self.indy_user

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
            self.teacher_request,
            init_kwargs={
                "student_id": None,
            },
        )

    def test_indy__not_any_student(self):
        """
        Independent is not any student.
        """

        self.assert_not_has_permission(
            self.indy_request,
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
            self.student_request,
            init_kwargs={
                "student_id": None,
            },
        )

    def test_student__specific_student(self):
        """
        Student is a specific student.
        """

        self.assert_has_permission(
            self.student_request,
            init_kwargs={
                "student_id": self.student.id,
            },
        )

    def test_student__not_specific_student(self):
        """
        Student is not a specific student.
        """

        student = Student.objects.exclude(id=self.student.id).first()
        assert student is not None

        self.assert_not_has_permission(
            self.student_request,
            init_kwargs={
                "student_id": student.id,
            },
        )
