import typing as t

from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ....tests import APIClient, APITestCase
from ...models import Class, School, Student, Teacher, User
from ...serializers import SchoolSerializer
from ...views import SchoolViewSet


class TestSchoolViewSet(APITestCase):
    """
    Base naming convention:
        test_{action}

    action: The view set action.
        https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions
    """

    fixtures = [
        "users",
        "teachers",
        "schools",
        "classes",
        "students",
    ]

    def _login_teacher(self):
        return self.client.login_teacher(
            email="alberteinstein@codeforlife.com",
            password="Password1",
            is_admin=True,
        )

    def _login_student(self):
        return self.client.login_student(
            email="leonardodavinci@codeforlife.com",
            password="Password1",
        )

    def _login_indy_student(self):
        return self.client.login_indy_student(
            email="indianajones@codeforlife.com",
            password="Password1",
        )

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

    def _retrieve_school(
        self,
        school: School,
        status_code_assertion: APIClient.StatusCodeAssertion = None,
    ):
        return self.client.retrieve(
            "school",
            school,
            SchoolSerializer,
            status_code_assertion,
        )

    def test_retrieve__indy_student(self):
        """
        Independent student cannot retrieve any school.
        """

        self._login_indy_student()

        school = School.objects.first()
        assert school

        self._retrieve_school(
            school,
            status_code_assertion=status.HTTP_403_FORBIDDEN,
        )

    def test_retrieve__teacher__same_school(self):
        """
        Teacher can retrieve the same school they are in.
        """

        user = self._login_teacher()

        self._retrieve_school(user.teacher.school)

    def test_retrieve__student__same_school(self):
        """
        Student can retrieve the same school they are in.
        """

        user = self._login_student()

        self._retrieve_school(user.student.class_field.teacher.school)

    def test_retrieve__teacher__not_same_school(self):
        """
        Teacher cannot retrieve a school they are not in.
        """

        user = self._login_teacher()

        school = School.objects.exclude(id=user.teacher.school.id).first()
        assert school

        self._retrieve_school(
            school,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve__student__not_same_school(self):
        """
        Student cannot retrieve a school they are not in.
        """

        user = self._login_student()

        school = School.objects.exclude(
            id=user.student.class_field.teacher.school.id
        ).first()
        assert school

        self._retrieve_school(
            school,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    """
    List naming convention:
        test_list__{user_type}

    user_type: The type of user that is making the request. Options:
        - teacher: A teacher.
        - student: A school student.
        - indy_student: A non-school student.
    """

    def _list_schools(
        self,
        schools: t.Iterable[School],
        status_code_assertion: APIClient.StatusCodeAssertion = None,
    ):
        return self.client.list(
            "school",
            schools,
            SchoolSerializer,
            status_code_assertion,
        )

    def test_list__indy_student(self):
        """
        Independent student cannot list any schools.
        """

        self._login_indy_student()

        self._list_schools(
            [],
            status_code_assertion=status.HTTP_403_FORBIDDEN,
        )

    def test_list__teacher(self):
        """
        Teacher can list only the school they are in.
        """

        user = self._login_teacher()

        self._list_schools([user.teacher.school])

    def test_list__student(self):
        """
        Student can list only the school they are in.
        """

        user = self._login_student()

        self._list_schools([user.student.class_field.teacher.school])

    """
    General tests that apply to all actions.
    """

    def test_all__requires_authentication(self):
        """
        User must be authenticated to call any endpoint.
        """

        assert IsAuthenticated in SchoolViewSet.permission_classes

    def test_all__only_http_get(self):
        """
        These model are read-only.
        """

        assert [name.lower() for name in SchoolViewSet.http_method_names] == [
            "get"
        ]
