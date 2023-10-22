import typing as t

from rest_framework import status

from ....tests import APITestCase, APIClient
from ...serializers import SchoolSerializer
from ...models import User, School, Teacher, Student, Class, UserProfile


class TestSchoolViewSet(APITestCase):
    """
    Base naming convention:
        test_{action}

    action: The view set action.
        https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions
    """

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

    def _login_teacher(self):
        return self.login_teacher(
            email="alberteinstein@codeforlife.com",
            password="Password1",
        )

    def _login_student(self):
        return self.login_student(
            email="leonardodavinci@codeforlife.com",
            password="Password1",
        )

    """
    Retrieve naming convention:
        test_retrieve__{user_type}__{same_school}

    user_type: The type of user that is making the request. Options:
        - teacher: A teacher.
        - student: A school student.
    
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
        Teacher can not retrieve a school they are not in.
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
        Student can not retrieve a school they are not in.
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
