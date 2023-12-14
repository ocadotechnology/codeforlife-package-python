import typing as t

from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ....tests import APIClient, APITestCase
from ...models import Class, School, Student, Teacher, User
from ...serializers import UserSerializer
from ...views import UserViewSet


class TestUserViewSet(APITestCase):
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
            email="jane.doe@codeforlife.com",
            password="password",
            is_admin=False,
        )

    def _login_admin_teacher(self):
        return self.client.login_teacher(
            email="john.doe@codeforlife.com",
            password="password",
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
        test_retrieve__{user_type}__{other_user_type}__{same_school}__{same_class}

    user_type: The type of user that is making the request. Options:
        - teacher: A non-admin teacher.
        - admin_teacher: An admin teacher.
        - student: A school student.
        - indy_student: A non-school student.

    other_user_type: The type of user whose data is being requested. Options:
        - self: User's own data.
        - teacher: Another teacher's data.
        - student: Another student's data.

    same_school: A flag for if the other user is from the same school. Options:
        - same_school: The other user is from the same school.
        - not_same_school: The other user is not from the same school.

    same_class: A flag for if the other user is from the same class. Options:
        - same_class: The other user is from the same class.
        - not_same_class: The other user is not from the same class.
    """

    def _retrieve_user(
        self,
        user: User,
        status_code_assertion: APIClient.StatusCodeAssertion = None,
    ):
        return self.client.retrieve(
            "user",
            user,
            UserSerializer,
            status_code_assertion,
        )

    def test_retrieve__teacher__self(self):
        """
        Teacher can retrieve their own user data.
        """

        user = self._login_teacher()

        self._retrieve_user(user)

    def test_retrieve__student__self(self):
        """
        Student can retrieve their own user data.
        """

        user = self._login_student()

        self._retrieve_user(user)

    def test_retrieve__indy_student__self(self):
        """
        Independent student can retrieve their own user data.
        """

        user = self._login_indy_student()

        self._retrieve_user(user)

    def test_retrieve__teacher__teacher__same_school(self):
        """
        Teacher can retrieve another teacher from the same school.
        """

        user = self._login_teacher()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.exclude(id=user.id).filter(
                new_teacher__school=user.teacher.school
            ),
            is_teacher=True,
            same_school=True,
        )

        self._retrieve_user(other_user)

    def test_retrieve__teacher__student__same_school__same_class(self):
        """
        Teacher can retrieve a student from the same school and class.
        """

        user = self._login_teacher()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.filter(
                new_student__class_field__teacher__school=user.teacher.school,
                new_student__class_field__teacher=user.teacher,
            ),
            is_teacher=False,
            same_school=True,
            same_class=True,
        )

        self._retrieve_user(other_user)

    def test_retrieve__teacher__student__same_school__not_same_class(self):
        """
        Teacher cannot retrieve a student from the same school and a different
        class.
        """

        user = self._login_teacher()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.filter(
                new_student__class_field__teacher__school=user.teacher.school
            ).exclude(new_student__class_field__teacher=user.teacher),
            is_teacher=False,
            same_school=True,
            same_class=False,
        )

        self._retrieve_user(
            other_user,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve__admin_teacher__student__same_school__same_class(self):
        """
        Admin teacher can retrieve a student from the same school and class.
        """

        user = self._login_admin_teacher()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.filter(
                new_student__class_field__teacher__school=user.teacher.school,
                new_student__class_field__teacher=user.teacher,
            ),
            is_teacher=False,
            same_school=True,
            same_class=True,
        )

        self._retrieve_user(other_user)

    def test_retrieve__admin_teacher__student__same_school__not_same_class(
        self,
    ):
        """
        Admin teacher can retrieve a student from the same school and a
        different class.
        """

        user = self._login_admin_teacher()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.filter(
                new_student__class_field__teacher__school=user.teacher.school
            ).exclude(new_student__class_field__teacher=user.teacher),
            is_teacher=False,
            same_school=True,
            same_class=False,
        )

        self._retrieve_user(other_user)

    def test_retrieve__student__teacher__same_school__same_class(self):
        """
        Student cannot retrieve a teacher from the same school and class.
        """

        user = self._login_student()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.filter(
                new_teacher__school=user.student.class_field.teacher.school,
                new_teacher__class_teacher=user.student.class_field,
            ),
            is_teacher=True,
            same_school=True,
            same_class=True,
        )

        self._retrieve_user(
            other_user,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve__student__teacher__same_school__not_same_class(self):
        """
        Student cannot retrieve a teacher from the same school and a different
        class.
        """

        user = self._login_student()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.filter(
                new_teacher__school=user.student.class_field.teacher.school
            ).exclude(new_teacher__class_teacher=user.student.class_field),
            is_teacher=True,
            same_school=True,
            same_class=False,
        )

        self._retrieve_user(
            other_user,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve__student__student__same_school__same_class(self):
        """
        Student can retrieve another student from the same school and class.
        """

        user = self._login_student()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.exclude(id=user.id).filter(
                new_student__class_field__teacher__school=user.student.class_field.teacher.school,
                new_student__class_field=user.student.class_field,
            ),
            is_teacher=False,
            same_school=True,
            same_class=True,
        )

        self._retrieve_user(other_user)

    def test_retrieve__student__student__same_school__not_same_class(self):
        """
        Student cannot retrieve another student from the same school and a
        different class.
        """

        user = self._login_student()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.exclude(id=user.id)
            .filter(
                new_student__class_field__teacher__school=user.student.class_field.teacher.school,
            )
            .exclude(new_student__class_field=user.student.class_field),
            is_teacher=False,
            same_school=True,
            same_class=False,
        )

        self._retrieve_user(
            other_user,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve__teacher__teacher__not_same_school(self):
        """
        Teacher cannot retrieve another teacher from another school.
        """

        user = self._login_teacher()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.exclude(
                new_teacher__school=user.teacher.school
            ).filter(new_teacher__school__isnull=False),
            is_teacher=True,
            same_school=False,
        )

        self._retrieve_user(
            other_user,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve__teacher__student__not_same_school(self):
        """
        Teacher cannot retrieve a student from another school.
        """

        user = self._login_teacher()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.exclude(
                new_student__class_field__teacher__school=user.teacher.school
            ).filter(new_student__class_field__teacher__school__isnull=False),
            is_teacher=False,
            same_school=False,
        )

        self._retrieve_user(
            other_user,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve__student__teacher__not_same_school(self):
        """
        Student cannot retrieve a teacher from another school.
        """

        user = self._login_student()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.exclude(
                new_teacher__school=user.student.class_field.teacher.school
            ).filter(new_teacher__school__isnull=False),
            is_teacher=True,
            same_school=False,
        )

        self._retrieve_user(
            other_user,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve__student__student__not_same_school(self):
        """
        Student cannot retrieve another student from another school.
        """

        user = self._login_student()

        other_user = self.get_another_school_user(
            user,
            other_users=User.objects.exclude(
                new_student__class_field__teacher__school=user.student.class_field.teacher.school
            ).filter(new_student__class_field__teacher__school__isnull=False),
            is_teacher=False,
            same_school=False,
        )

        self._retrieve_user(
            other_user,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve__indy_student__teacher(self):
        """
        Independent student cannot retrieve a teacher.
        """

        user = self._login_indy_student()

        other_user = self.get_other_school_user(
            user,
            other_users=User.objects.filter(new_teacher__school__isnull=False),
            is_teacher=True,
        )

        self._retrieve_user(
            other_user,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    def test_retrieve__indy_student__student(self):
        """
        Independent student cannot retrieve a student.
        """

        user = self._login_indy_student()

        other_user = self.get_other_school_user(
            user,
            other_users=User.objects.filter(
                new_student__class_field__teacher__school__isnull=False
            ),
            is_teacher=False,
        )

        self._retrieve_user(
            other_user,
            status_code_assertion=status.HTTP_404_NOT_FOUND,
        )

    """
    List naming convention:
        test_list__{user_type}__{filters}

    user_type: The type of user that is making the request. Options:
        - teacher: A teacher.
        - student: A school student.
        - indy_student: A non-school student.

    filters: Any search params used to dynamically filter the list.
    """

    def _list_users(
        self,
        users: t.Iterable[User],
        status_code_assertion: APIClient.StatusCodeAssertion = None,
        filters: APIClient.ListFilters = None,
    ):
        return self.client.list(
            "user",
            users,
            UserSerializer,
            status_code_assertion,
            filters,
        )

    def test_list__teacher(self):
        """
        Teacher can list all the users in the same school.
        """

        user = self._login_teacher()

        self._list_users(
            User.objects.filter(new_teacher__school=user.teacher.school)
            | User.objects.filter(
                new_student__class_field__teacher__school=user.teacher.school,
                new_student__class_field__teacher=user.teacher,
            )
        )

    def test_list__teacher__students_in_class(self):
        """
        Teacher can list all the users in a class they own.
        """

        user = self._login_teacher()

        klass = user.teacher.class_teacher.first()
        assert klass

        self._list_users(
            User.objects.filter(new_student__class_field=klass),
            filters={"students_in_class": klass.id},
        )

    def test_list__student(self):
        """
        Student can list only themself.
        """

        user = self._login_student()

        self._list_users([user])

    def test_list__indy_student(self):
        """
        Independent student can list only themself.
        """

        user = self._login_indy_student()

        self._list_users([user])

    """
    General tests that apply to all actions.
    """

    def test_all__requires_authentication(self):
        """
        User must be authenticated to call any endpoint.
        """

        assert IsAuthenticated in UserViewSet.permission_classes

    def test_all__only_http_get(self):
        """
        These model are read-only.
        """

        assert [name.lower() for name in UserViewSet.http_method_names] == [
            "get"
        ]
