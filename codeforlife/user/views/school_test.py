"""
© Ocado Group
Created on 20/01/2024 at 09:47:30(+00:00).
"""

from ...permissions import OR, AllowNone
from ...tests import ModelViewSetTestCase
from ..models import (
    IndependentUser,
    School,
    SchoolTeacherUser,
    StudentUser,
    User,
)
from ..permissions import IsIndependent, IsStudent, IsTeacher
from ..views import SchoolViewSet

RequestUser = User


# pylint: disable-next=too-many-ancestors,missing-class-docstring
class TestSchoolViewSet(ModelViewSetTestCase[RequestUser, School]):
    basename = "school"
    model_view_set_class = SchoolViewSet
    fixtures = ["school_1", "independent"]

    # test: get permissions

    def test_get_permissions__list(self):
        """No one can list schools."""
        self.assert_get_permissions(
            permissions=[AllowNone()],
            action="list",
        )

    def test_get_permissions__retrieve(self):
        """Only student and school-teachers can retrieve a school."""
        self.assert_get_permissions(
            permissions=[
                OR(
                    OR(IsStudent(), IsTeacher(in_school=True)),
                    IsIndependent(is_requesting_to_join_class=True),
                )
            ],
            action="retrieve",
        )

    # test: get queryset

    def test_get_queryset__teacher(self):
        """A school-teacher-user can only target the school they are in."""
        user = SchoolTeacherUser.objects.first()
        assert user

        self.assert_get_queryset(
            values=[user.teacher.school],
            request=self.client.request_factory.get(user=user),
        )

    def test_get_queryset__student(self):
        """A student-user can only target the school they are in."""
        user = StudentUser.objects.first()
        assert user

        self.assert_get_queryset(
            values=[user.student.class_field.teacher.school],
            request=self.client.request_factory.get(user=user),
        )

    def test_get_queryset__independent(self):
        """
        An independent-user can only target the school they are requesting
        to join.
        """
        user = IndependentUser.objects.filter(
            new_student__pending_class_request__isnull=False
        ).first()
        assert user

        self.assert_get_queryset(
            values=[user.student.pending_class_request.teacher.school],
            request=self.client.request_factory.get(user=user),
        )

    # test: actions

    def test_retrieve(self):
        """Can successfully retrieve a school."""
        user = SchoolTeacherUser.objects.first()
        assert user

        self.client.login_as(user, password="abc123")
        self.client.retrieve(model=user.teacher.school)
