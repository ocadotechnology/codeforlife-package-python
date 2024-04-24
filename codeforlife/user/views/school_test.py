"""
© Ocado Group
Created on 20/01/2024 at 09:47:30(+00:00).
"""


from ...permissions import OR, AllowNone
from ...tests import ModelViewSetTestCase
from ..models import School, SchoolTeacherUser, StudentUser, User
from ..permissions import IsStudent, IsTeacher
from ..views import SchoolViewSet

RequestUser = User


# pylint: disable-next=too-many-ancestors,missing-class-docstring
class TestSchoolViewSet(ModelViewSetTestCase[RequestUser, School]):
    basename = "school"
    model_view_set_class = SchoolViewSet

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
            permissions=[OR(IsStudent(), IsTeacher(in_school=True))],
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

    # test: actions

    def test_retrieve(self):
        """Can successfully retrieve a school."""
        user = SchoolTeacherUser.objects.first()
        assert user

        self.client.login_as(user, password="abc123")
        self.client.retrieve(model=user.teacher.school)
