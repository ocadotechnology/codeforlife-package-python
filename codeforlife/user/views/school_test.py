"""
© Ocado Group
Created on 20/01/2024 at 09:47:30(+00:00).
"""

from rest_framework import status

from ...permissions import OR, AllowNone
from ...tests import ModelViewSetTestCase
from ..models import Class, School, Student, Teacher, User, UserProfile
from ..permissions import IsStudent, IsTeacher
from ..views import SchoolViewSet

RequestUser = User


# pylint: disable-next=too-many-ancestors
class TestSchoolViewSet(ModelViewSetTestCase[RequestUser, School]):
    """
    Base naming convention:
        test_{action}

    action: The view set action.
        https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions
    """

    basename = "school"
    model_view_set_class = SchoolViewSet

    # TODO: replace this setup with data fixtures.
    def setUp(self):
        school = School.objects.create(
            name="ExampleSchool",
            country="UK",
        )

        user = User.objects.create(
            first_name="Example",
            last_name="Teacher",
            email="example.teacher@codeforlife.com",
            username="example.teacher@codeforlife.com",
        )

        user_profile = UserProfile.objects.create(user=user)

        teacher = Teacher.objects.create(
            user=user_profile,
            new_user=user,
            school=school,
        )

        klass = Class.objects.create(
            name="ExampleClass",
            teacher=teacher,
            created_by=teacher,
        )

        user = User.objects.create(
            first_name="Example",
            last_name="Student",
            email="example.student@codeforlife.com",
            username="example.student@codeforlife.com",
        )

        user_profile = UserProfile.objects.create(user=user)

        Student.objects.create(
            class_field=klass,
            user=user_profile,
            new_user=user,
        )

    def _login_admin_school_teacher(self):
        return self.client.login_admin_school_teacher(
            email="alberteinstein@codeforlife.com",
            password="Password1",
        )

    def _login_student(self):
        return self.client.login_student(
            first_name="Leonardo",
            password="Password1",
            class_id="AB123",
        )

    def _login_indy(self):
        return self.client.login_indy(
            email="indianajones@codeforlife.com",
            password="Password1",
        )

    # pylint: disable-next=pointless-string-statement
    """
    Retrieve naming convention:
        test_retrieve__{user_type}__{same_school}

    user_type: The type of user that is making the request. Options:
        - teacher: A teacher.
        - student: A school student.
        - indy_student: A non-school student.

    same_school: A flag for if the school is the same school that the user
        is in. Options:
        - same_school: The other user is from the same school.
        - not_same_school: The other user is not from the same school.
    """

    def test_retrieve__indy_student(self):
        """
        Independent student cannot retrieve any school.
        """

        self._login_indy()

        school = School.objects.first()
        assert school

        self.client.retrieve(school, status.HTTP_403_FORBIDDEN)

    def test_retrieve__teacher__same_school(self):
        """
        Teacher can retrieve the same school they are in.
        """

        user = self._login_admin_school_teacher()

        self.client.retrieve(user.teacher.school)

    def test_retrieve__student__same_school(self):
        """
        Student can retrieve the same school they are in.
        """

        user = self._login_student()

        self.client.retrieve(user.student.class_field.teacher.school)

    def test_retrieve__teacher__not_same_school(self):
        """
        Teacher cannot retrieve a school they are not in.
        """

        user = self._login_admin_school_teacher()

        school = School.objects.exclude(id=user.teacher.school.id).first()
        assert school

        self.client.retrieve(school, status.HTTP_404_NOT_FOUND)

    def test_retrieve__student__not_same_school(self):
        """
        Student cannot retrieve a school they are not in.
        """

        user = self._login_student()

        school = School.objects.exclude(
            id=user.student.class_field.teacher.school.id
        ).first()
        assert school

        self.client.retrieve(school, status.HTTP_404_NOT_FOUND)

    # pylint: disable-next=pointless-string-statement
    """
    List naming convention:
        test_list__{user_type}

    user_type: The type of user that is making the request. Options:
        - teacher: A teacher.
        - student: A school student.
        - indy_student: A non-school student.
    """

    def test_list__indy_student(self):
        """
        Independent student cannot list any schools.
        """

        self._login_indy()

        self.client.list([], status.HTTP_403_FORBIDDEN)

    # TODO: replace above tests with get_queryset() tests

    def test_get_permissions__list(self):
        """
        No one is allowed to list schools.
        """

        self.assert_get_permissions(
            permissions=[AllowNone()],
            action="list",
        )

    def test_get_permissions__retrieve(self):
        """
        Only a user in a school can retrieve a school.
        """

        self.assert_get_permissions(
            permissions=[OR(IsStudent(), IsTeacher(in_school=True))],
            action="retrieve",
        )
