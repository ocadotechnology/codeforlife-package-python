"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from django.contrib.auth.models import AnonymousUser

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

        self.admin_teacher_user = User.objects.get(pk=1)
        assert (
            self.admin_teacher_user.teacher
            and self.admin_teacher_user.teacher.is_admin
        )
        self.admin_teacher = self.admin_teacher_user.teacher
        self.admin_teacher_request = self.request_factory.get("/")
        self.admin_teacher_request.user = self.admin_teacher_user

        self.non_admin_teacher_user = User.objects.get(pk=2)
        assert (
            self.non_admin_teacher_user.teacher
            and not self.non_admin_teacher_user.teacher.is_admin
        )
        self.non_admin_teacher = self.non_admin_teacher_user.teacher
        self.non_admin_teacher_request = self.request_factory.get("/")
        self.non_admin_teacher_request.user = self.non_admin_teacher_user

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
            self.admin_teacher_request,
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
            self.admin_teacher_request,
            init_kwargs={
                "teacher_id": None,
                "is_admin": True,
            },
        )

        self.assert_not_has_permission(
            self.non_admin_teacher_request,
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
            self.admin_teacher_request,
            init_kwargs={
                "teacher_id": None,
                "is_admin": False,
            },
        )

        self.assert_has_permission(
            self.non_admin_teacher_request,
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
            self.admin_teacher_request,
            init_kwargs={
                "teacher_id": self.admin_teacher.id,
                "is_admin": None,
            },
        )

        self.assert_not_has_permission(
            self.admin_teacher_request,
            init_kwargs={
                "teacher_id": self.non_admin_teacher.id,
                "is_admin": None,
            },
        )

    def test_id__true(self):
        """
        Is a specific admin teacher.
        """

        self.assert_has_permission(
            self.admin_teacher_request,
            init_kwargs={
                "teacher_id": self.admin_teacher.id,
                "is_admin": True,
            },
        )

        self.assert_not_has_permission(
            self.non_admin_teacher_request,
            init_kwargs={
                "teacher_id": self.non_admin_teacher.id,
                "is_admin": True,
            },
        )

    def test_id__false(self):
        """
        Is a specific non-admin teacher.
        """

        self.assert_not_has_permission(
            self.admin_teacher_request,
            init_kwargs={
                "teacher_id": self.admin_teacher.id,
                "is_admin": False,
            },
        )

        self.assert_has_permission(
            self.non_admin_teacher_request,
            init_kwargs={
                "teacher_id": self.non_admin_teacher.id,
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
        - anon: An anonymous user.
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

    def test_anon(self):
        """
        Anonymous user is not a teacher.
        """

        request = self.request_factory.get("/")
        request.user = AnonymousUser()

        self.assert_not_has_permission(request)
