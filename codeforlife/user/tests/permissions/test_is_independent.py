"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from django.contrib.auth.models import AnonymousUser

from ....tests import PermissionTestCase
from ...models import User
from ...permissions import IsIndependent


# pylint: disable-next=missing-class-docstring
class TestIsIndependent(PermissionTestCase[IsIndependent]):
    fixtures = [
        "users",
        "teachers",
        "schools",
        "classes",
        "students",
    ]

    # pylint: disable-next=pointless-string-statement
    """
    Naming convention:
        test_{user_type}

    user_type: The type of user. Options:
        - teacher: A teacher.
        - student: A student.
        - indy: An independent.
        - anon: An anonymous user.
    """

    def test_teacher(self):
        """
        Teacher is not any independent.
        """

        user = User.objects.get(pk=1)
        assert user.teacher

        request = self.request_factory.get("/")
        request.user = user

        self.assert_not_has_permission(request)

    def test_student(self):
        """
        Student is not any independent.
        """

        user = User.objects.get(pk=3)
        assert user.student

        request = self.request_factory.get("/")
        request.user = user

        self.assert_not_has_permission(request)

    def test_indy(self):
        """
        Independent is any independent.
        """

        user = User.objects.get(pk=5)
        assert not user.teacher and not user.student

        request = self.request_factory.get("/")
        request.user = user

        self.assert_has_permission(request)

    def test_anon(self):
        """
        Anonymous user is not any independent.
        """

        request = self.request_factory.get("/")
        request.user = AnonymousUser()

        self.assert_not_has_permission(request)
