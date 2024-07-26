"""
© Ocado Group
Created on 20/01/2024 at 09:48:30(+00:00).
"""

from ...permissions import OR
from ...tests import ModelViewSetTestCase
from ..models import (
    AdminSchoolTeacherUser,
    Class,
    NonAdminSchoolTeacherUser,
    StudentUser,
    User,
)
from ..permissions import IsStudent, IsTeacher
from ..views import ClassViewSet

RequestUser = User


# pylint: disable-next=too-many-ancestors,missing-class-docstring
class TestClassViewSet(ModelViewSetTestCase[RequestUser, Class]):
    basename = "class"
    model_view_set_class = ClassViewSet
    fixtures = ["school_1"]

    def setUp(self):
        self.admin_school_teacher_user = AdminSchoolTeacherUser.objects.get(
            email="admin.teacher@school1.com"
        )

    # test: get permissions

    def test_get_permissions__list(self):
        """Only school-teachers can list classes."""
        self.assert_get_permissions(
            permissions=[
                OR(IsTeacher(is_admin=True), IsTeacher(in_class=True))
            ],
            action="list",
        )

    def test_get_permissions__retrieve(self):
        """Anyone in a school can retrieve a class."""
        self.assert_get_permissions(
            permissions=[
                OR(
                    IsStudent(),
                    OR(IsTeacher(is_admin=True), IsTeacher(in_class=True)),
                )
            ],
            action="retrieve",
        )

    # test: get queryset

    def test_get_queryset__student(self):
        """Student-users can only target classes they are in."""
        user = StudentUser.objects.first()
        assert user

        self.assert_get_queryset(
            values=[user.student.class_field],
            request=self.client.request_factory.get(user=user),
        )

    def test_get_queryset__teacher__admin(self):
        """
        Admin-teacher-users can only target all the classes in their school.
        """
        user = AdminSchoolTeacherUser.objects.first()
        assert user

        self.assert_get_queryset(
            values=user.teacher.classes,
            request=self.client.request_factory.get(user=user),
        )

    def test_get_queryset__teacher__non_admin(self):
        """
        Non-admin-teacher-users can only target all the classes they teach.
        """
        user = NonAdminSchoolTeacherUser.objects.first()
        assert user

        self.assert_get_queryset(
            values=user.teacher.classes,
            request=self.client.request_factory.get(user=user),
        )

    # test: actions

    def test_retrieve(self):
        """Can successfully retrieve a class."""
        user = StudentUser.objects.first()
        assert user

        self.client.login_as(user, password="Password1")
        self.client.retrieve(model=user.student.class_field)

    def test_list(self):
        """Can successfully list classes."""
        user = self.admin_school_teacher_user
        # TODO: assert user has classes in new schema.
        assert user.teacher.classes.count() >= 2

        self.client.login_as(user)
        self.client.list(models=user.teacher.classes.all())

    def test_list__teacher(self):
        """Can successfully list classes assigned to a teacher."""
        user = self.admin_school_teacher_user
        classes = Class.objects.filter(teacher=user.teacher)
        assert classes.exists()

        self.client.login_as(user)
        self.client.list(
            models=classes,
            filters={"teacher": str(user.teacher.id)},
        )
