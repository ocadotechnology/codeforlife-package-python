"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from django.contrib.auth.models import AnonymousUser

from ....tests import PermissionTestCase
from ...models import Class, User
from ...permissions import InClass


# pylint: disable-next=missing-class-docstring,too-many-instance-attributes
class TestInClass(PermissionTestCase[InClass]):
    fixtures = [
        "users",
        "teachers",
        "schools",
        "classes",
        "students",
    ]

    def setUp(self):
        super().setUp()

        self.class_teacher_user = User.objects.get(pk=1)
        assert (
            self.class_teacher_user.teacher
            and self.class_teacher_user.teacher.classes.exists()
        )
        self.class_teacher__classes = self.class_teacher_user.teacher.classes
        self.class_teacher_request = self.request_factory.get("/")
        self.class_teacher_request.user = self.class_teacher_user

        self.student_user = User.objects.get(pk=3)
        assert self.student_user.student
        self.student__class = self.student_user.student.klass
        self.student_request = self.request_factory.get("/")
        self.student_request.user = self.student_user

        self.indy_user = User.objects.get(pk=5)
        assert not self.indy_user.teacher and not self.indy_user.student
        self.indy_request = self.request_factory.get("/")
        self.indy_request.user = self.indy_user

        self.non_class_teacher_user = User.objects.get(pk=6)
        assert (
            self.non_class_teacher_user.teacher
            and not self.non_class_teacher_user.teacher.classes.exists()
        )
        self.non_class_teacher_request = self.request_factory.get("/")
        self.non_class_teacher_request.user = self.non_class_teacher_user

        self.anon_request = self.request_factory.get("/")
        self.anon_request.user = AnonymousUser()

    # pylint: disable-next=pointless-string-statement
    """
    Naming convention:
        test_{class_id}__{user_type}

    class_id: The id of a class. Options:
        - in_any_class: The user is in any class.
        - not_in_any_class: The user is not in any class.
        - in_class: A specific class the user is in.
        - not_in_class: A specific class the user is not in.

    user_type: The type of user. Options:
        - non_class_teacher: A teacher not in a class.
        - class_teacher: A teacher in a class.
        - student: A student.
        - indy: An independent.
        - anon: An anonymous user.
    """

    def test_in_any_class__class_teacher(self):
        """
        Teacher with a class is in any class.
        """

        self.assert_has_permission(
            self.class_teacher_request,
            init_kwargs={
                "class_id": None,
            },
        )

    def test_in_any_class__student(self):
        """
        Student is in any class.
        """

        self.assert_has_permission(
            self.student_request,
            init_kwargs={
                "class_id": None,
            },
        )

    def test_not_in_any_class__non_class_teacher(self):
        """
        Teacher without a class is not in any class.
        """

        self.assert_not_has_permission(
            self.non_class_teacher_request,
            init_kwargs={
                "class_id": None,
            },
        )

    def test_not_in_any_class__indy(self):
        """
        Independent is not in any class.
        """

        self.assert_not_has_permission(
            self.indy_request,
            init_kwargs={
                "class_id": None,
            },
        )

    def test_not_in_any_class__anon(self):
        """
        Anonymous user is not in any class.
        """

        self.assert_not_has_permission(
            self.anon_request,
            init_kwargs={
                "class_id": None,
            },
        )

    def test_in_class__class_teacher(self):
        """
        Teacher with a class is in a specific class.
        """

        klass = self.class_teacher__classes.first()
        assert klass is not None

        self.assert_has_permission(
            self.class_teacher_request,
            init_kwargs={
                "class_id": klass.id,
            },
        )

    def test_in_class__student(self):
        """
        Student is in a specific class.
        """

        self.assert_has_permission(
            self.student_request,
            init_kwargs={
                "class_id": self.student__class.id,
            },
        )

    def test_not_in_class__non_class_teacher(self):
        """
        Teacher without a class is not in a specific class.
        """

        klass = Class.objects.first()
        assert klass is not None

        self.assert_not_has_permission(
            self.non_class_teacher_request,
            init_kwargs={
                "class_id": klass.id,
            },
        )

    def test_not_in_class__class_teacher(self):
        """
        Teacher with a class is not in a specific class.
        """

        klass = Class.objects.difference(
            self.class_teacher__classes.all()
        ).first()
        assert klass is not None

        self.assert_not_has_permission(
            self.class_teacher_request,
            init_kwargs={
                "class_id": klass.id,
            },
        )

    def test_not_in_class__student(self):
        """
        Student is not in a specific class.
        """

        klass = Class.objects.exclude(id=self.student__class.id).first()
        assert klass is not None

        self.assert_not_has_permission(
            self.student_request,
            init_kwargs={
                "class_id": klass.id,
            },
        )

    def test_not_in_class__indy(self):
        """
        Independent is not in a specific class.
        """

        klass = Class.objects.first()
        assert klass is not None

        self.assert_not_has_permission(
            self.indy_request,
            init_kwargs={
                "class_id": klass.id,
            },
        )

    def test_not_in_class__anon(self):
        """
        Anonymous user is not in a specific class.
        """

        klass = Class.objects.first()
        assert klass is not None

        self.assert_not_has_permission(
            self.anon_request,
            init_kwargs={
                "class_id": klass.id,
            },
        )
