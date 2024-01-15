"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from ....tests import PermissionTestCase
from ...models import User
from ...permissions import IsTeacher


# pylint: disable-next=missing-class-docstring
class TestIsTeacher(PermissionTestCase[IsTeacher]):
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
        self.user__2 = User.objects.get(pk=2)

        assert self.user__1.teacher and self.user__1.teacher.is_admin
        assert self.user__2.teacher and not self.user__2.teacher.is_admin

        self.user__1__teacher = self.user__1.teacher
        self.user__2__teacher = self.user__2.teacher

        self.request__1 = self.request_factory.get("/")
        self.request__1.user = self.user__1
        self.request__2 = self.request_factory.get("/")
        self.request__2.user = self.user__2

    # pylint: disable-next=pointless-string-statement
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

    def test_none__none(self):
        """
        Is any teacher.
        """

        self.assert_has_permission(
            self.request__1,
            init_kwargs={
                "teacher_id": None,
                "is_admin": None,
            },
        )

    def test_none__true(self):
        """
        Is any admin teacher.
        """

        self.assert_has_permission(
            self.request__1,
            init_kwargs={
                "teacher_id": None,
                "is_admin": True,
            },
        )

        self.assert_not_has_permission(
            self.request__2,
            init_kwargs={
                "teacher_id": None,
                "is_admin": True,
            },
        )

    def test_none__false(self):
        """
        Is any non-admin teacher.
        """

        self.assert_not_has_permission(
            self.request__1,
            init_kwargs={
                "teacher_id": None,
                "is_admin": False,
            },
        )

        self.assert_has_permission(
            self.request__2,
            init_kwargs={
                "teacher_id": None,
                "is_admin": False,
            },
        )

    def test_id__none(self):
        """
        Is a specific teacher.
        """

        self.assert_has_permission(
            self.request__1,
            init_kwargs={
                "teacher_id": self.user__1__teacher.id,
                "is_admin": None,
            },
        )

        self.assert_not_has_permission(
            self.request__1,
            init_kwargs={
                "teacher_id": self.user__2__teacher.id,
                "is_admin": None,
            },
        )

    def test_id__true(self):
        """
        Is a specific admin teacher.
        """

        self.assert_has_permission(
            self.request__1,
            init_kwargs={
                "teacher_id": self.user__1__teacher.id,
                "is_admin": True,
            },
        )

        self.assert_not_has_permission(
            self.request__2,
            init_kwargs={
                "teacher_id": self.user__2__teacher.id,
                "is_admin": True,
            },
        )

    def test_id__false(self):
        """
        Is a specific non-admin teacher.
        """

        self.assert_not_has_permission(
            self.request__1,
            init_kwargs={
                "teacher_id": self.user__1__teacher.id,
                "is_admin": False,
            },
        )

        self.assert_has_permission(
            self.request__2,
            init_kwargs={
                "teacher_id": self.user__2__teacher.id,
                "is_admin": False,
            },
        )

    # pylint: disable-next=pointless-string-statement
    """
    Naming convention:
        test_{user_type}
    
    user_type: The type of user making the request. Options:
        - student: A student user.
        - indy: An independent user.
    """

    def test_student(self):
        """
        Student is not a teacher.
        """

        user = User.objects.get(pk=3)
        assert user.student is not None

        request = self.request_factory.get("/")
        request.user = user

        self.assert_not_has_permission(request)

    def test_indy(self):
        """
        Independent is not a teacher.
        """

        user = User.objects.get(pk=5)
        assert user.student is None
        assert user.teacher is None

        request = self.request_factory.get("/")
        request.user = user

        self.assert_not_has_permission(request)
