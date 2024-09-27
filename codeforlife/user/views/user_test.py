"""
© Ocado Group
Created on 19/01/2024 at 17:15:56(+00:00).
"""

import typing as t

from django.db.models import Q
from django.db.models.query import QuerySet

from ...tests import ModelViewSetTestCase
from ..models import (
    AdminSchoolTeacherUser,
    Class,
    IndependentUser,
    NonAdminSchoolTeacherUser,
    NonSchoolTeacherUser,
    SchoolTeacherUser,
    Student,
    StudentUser,
    User,
)
from ..views import UserViewSet

RequestUser = User


# pylint: disable-next=too-many-ancestors,too-many-public-methods,missing-class-docstring
class TestUserViewSet(ModelViewSetTestCase[RequestUser, User]):
    basename = "user"
    model_view_set_class = UserViewSet
    fixtures = ["non_school_teacher", "school_1", "independent"]

    def setUp(self):
        self.admin_school_teacher_user = AdminSchoolTeacherUser.objects.get(
            email="admin.teacher@school1.com"
        )

    # test: get queryset

    def test_get_queryset__indy(self):
        """Independent-users can only target themselves."""
        user = IndependentUser.objects.first()
        assert user

        self.assert_get_queryset(
            values=[user],
            request=self.client.request_factory.get(user=user),
        )

    def test_get_queryset__student(self):
        """
        Student-users can only target themselves, their classmates and their
        teacher.
        """
        user = StudentUser.objects.first()
        assert user

        users = [
            user,
            user.student.class_field.teacher.new_user,
            *list(
                User.objects.exclude(pk=user.pk).filter(
                    new_student__in=user.student.class_field.students.all()
                )
            ),
        ]
        users.sort(key=lambda user: user.pk)

        self.assert_get_queryset(
            values=users,
            request=self.client.request_factory.get(user=user),
        )

    def test_get_queryset__teacher__non_school(self):
        """Non-school-teacher-users can only target themselves."""
        user = NonSchoolTeacherUser.objects.first()
        assert user

        self.assert_get_queryset(
            values=[user],
            request=self.client.request_factory.get(user=user),
        )

    def test_get_queryset__teacher__admin(self):
        """
        Admin-teacher-users can only target themselves, all teachers in their
        school and all student in their school.
        """
        user = AdminSchoolTeacherUser.objects.first()
        assert user

        users = [
            *list(user.teacher.school_teacher_users),
            *list(user.teacher.student_users),
        ]
        users.sort(key=lambda user: user.pk)

        self.assert_get_queryset(
            values=users,
            request=self.client.request_factory.get(user=user),
        )

    def test_get_queryset__teacher__non_admin(self):
        """
        Non-admin-teacher-users can only target themselves, all teachers in
        their school and their class-students.
        """
        user = NonAdminSchoolTeacherUser.objects.first()
        assert user

        users = [
            *list(
                SchoolTeacherUser.objects.filter(
                    new_teacher__school=user.teacher.school
                )
            ),
            *list(user.teacher.student_users),
        ]
        users.sort(key=lambda user: user.pk)

        self.assert_get_queryset(
            values=users,
            request=self.client.request_factory.get(user=user),
        )

    # test: actions

    def test_list(self):
        """Can successfully list users."""
        user = AdminSchoolTeacherUser.objects.first()
        assert user

        users = [
            *list(user.teacher.school_teacher_users),
            *list(user.teacher.student_users),
        ]
        users.sort(key=lambda user: user.pk)

        self.client.login_as(user, password="abc123")
        self.client.list(models=users)

    def test_list__students_in_class(self):
        """Can successfully list student-users in a class."""
        user = self.admin_school_teacher_user
        assert user.teacher.classes.count() >= 2

        klass = t.cast(Class, user.teacher.classes.first())
        students: QuerySet[Student] = klass.students.all()
        assert (
            Student.objects.filter(
                class_field__teacher__school=user.teacher.school
            )
            .exclude(pk__in=students.values_list("pk", flat=True))
            .exists()
        ), "There are no other students in other classes, in the same school."

        self.client.login_as(user)
        self.client.list(
            models=StudentUser.objects.filter(new_student__in=students),
            filters={"students_in_class": klass.access_code},
        )

    def test_list__type__teacher(self):
        """Can successfully list only teacher-users."""
        user = self.admin_school_teacher_user
        school_teacher_users = user.teacher.school_teacher_users.all()
        assert school_teacher_users.exists()

        self.client.login_as(user)
        self.client.list(
            models=school_teacher_users,
            filters={"type": "teacher"},
        )

    def test_list__type__student(self):
        """Can successfully list only student-users."""
        user = self.admin_school_teacher_user
        student_users = user.teacher.student_users.all()
        assert student_users.exists()

        self.client.login_as(user)
        self.client.list(
            models=student_users,
            filters={"type": "student"},
        )

    def test_list__type__indy(self):
        """Can successfully list only independent-users."""
        user = self.admin_school_teacher_user
        indy_users = user.teacher.indy_users.all()
        assert indy_users.exists()

        self.client.login_as(user)
        self.client.list(
            models=indy_users,
            filters={"type": "indy"},
        )

    def test_list___id(self):
        """Can successfully list all users in a school and exclude some IDs."""
        user = AdminSchoolTeacherUser.objects.first()
        assert user

        users = [
            *list(user.teacher.school_teacher_users),
            *list(user.teacher.student_users),
        ]
        users.sort(key=lambda user: user.pk)

        exclude_user_1: User = users.pop()
        exclude_user_2: User = users.pop()

        self.client.login_as(user, password="abc123")
        self.client.list(
            models=users,
            filters={
                "_id": [
                    str(exclude_user_1.id),
                    str(exclude_user_2.id),
                ]
            },
        )

    def test_list__name(self):
        """Can successfully list all users by name."""
        user = AdminSchoolTeacherUser.objects.first()
        assert user

        school_users = user.teacher.school_users
        first_name, last_name = user.first_name, user.last_name[:1]

        self.client.login_as(user, password="abc123")
        self.client.list(
            models=school_users.filter(
                Q(first_name__icontains=first_name)
                | Q(last_name__icontains=last_name)
            ).order_by("pk"),
            filters={"name": f"{first_name} {last_name}"},
        )

    def test_retrieve(self):
        """Can successfully retrieve users."""
        user = AdminSchoolTeacherUser.objects.first()
        assert user

        self.client.login_as(user, password="abc123")
        self.client.retrieve(model=user)
