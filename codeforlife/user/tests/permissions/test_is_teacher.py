"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from ....tests import APITestCase
from ...models import User
from ...permissions import IsTeacher


class TestIsTeacher(APITestCase):
    # TODO: test that students and independents do not get permission.
    """
    Naming convention:
        test_{teacher_id}__{is_admin}

    teacher_id: The id of a teacher. Options:
        - id: A specific teacher.
        - none: Any teacher.

    is_admin: A flag for if the teacher is an admin. Options:
        - true: Teacher is an admin.
        - false: Teacher is a non-admin.
        - none: Teacher is an admin or a non-admin.
    """

    fixtures = [
        "users",
        "teachers",
        "schools",
        "classes",
        "students",
    ]

    def setUp(self):
        self.user__1 = User.objects.get(pk=1)
        self.user__2 = User.objects.get(pk=2)

        assert self.user__1.teacher and self.user__1.teacher.is_admin
        assert self.user__2.teacher and not self.user__2.teacher.is_admin

        self.user__1__teacher = self.user__1.teacher
        self.user__2__teacher = self.user__2.teacher

        request_factory = APIRequestFactory()
        self.request__1 = request_factory.get("/")
        self.request__1.user = self.user__1
        self.request__2 = request_factory.get("/")
        self.request__2.user = self.user__2

    def test_none__none(self):
        """
        Is any teacher.
        """

        assert IsTeacher(
            teacher_id=None,
            is_admin=None,
        ).has_permission(self.request__1, APIView())

    def test_none__true(self):
        """
        Is any admin teacher.
        """

        assert IsTeacher(
            teacher_id=None,
            is_admin=True,
        ).has_permission(self.request__1, APIView())

        assert not IsTeacher(
            teacher_id=None,
            is_admin=True,
        ).has_permission(self.request__2, APIView())

    def test_none__false(self):
        """
        Is any non-admin teacher.
        """

        assert not IsTeacher(
            teacher_id=None,
            is_admin=False,
        ).has_permission(self.request__1, APIView())

        assert IsTeacher(
            teacher_id=None,
            is_admin=False,
        ).has_permission(self.request__2, APIView())

    def test_id__none(self):
        """
        Is a specific teacher.
        """

        assert IsTeacher(
            teacher_id=self.user__1__teacher.id,
            is_admin=None,
        ).has_permission(self.request__1, APIView())

        assert not IsTeacher(
            teacher_id=self.user__2__teacher.id,
            is_admin=None,
        ).has_permission(self.request__1, APIView())

    def test_id__true(self):
        """
        Is a specific admin teacher.
        """

        assert IsTeacher(
            teacher_id=self.user__1__teacher.id,
            is_admin=True,
        ).has_permission(self.request__1, APIView())

        assert not IsTeacher(
            teacher_id=self.user__2__teacher.id,
            is_admin=True,
        ).has_permission(self.request__2, APIView())

    def test_id__false(self):
        """
        Is a specific non-admin teacher.
        """

        assert not IsTeacher(
            teacher_id=self.user__1__teacher.id,
            is_admin=False,
        ).has_permission(self.request__1, APIView())

        assert IsTeacher(
            teacher_id=self.user__2__teacher.id,
            is_admin=False,
        ).has_permission(self.request__2, APIView())
