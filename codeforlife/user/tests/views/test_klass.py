from ....tests import APIClient, APITestCase
from ...models import Class
from ...serializers import ClassSerializer
from ...views import ClassViewSet


class TestClassViewSet(APITestCase):
    """
    Base naming convention:
        test_{action}

    action: The view set action.
        https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions
    """

    def _login_student(self):
        return self.client.login_student(
            email="leonardodavinci@codeforlife.com",
            password="Password1",
        )

    # pylint: disable-next=pointless-string-statement
    """
    Retrieve naming convention:
        test_retrieve__{user_type}__{same_school}__{in_class}

    user_type: The type of user that is making the request. Options:
        - teacher: A non-admin teacher.
        - admin_teacher: An admin teacher.
        - student: A school student.
        - indy_student: A non-school student.

    same_school: A flag for if the class is in the same school that the user is
        in. Options:
        - same_school: The class is in the same school as the user.
        - not_same_school: The class is not in the same school as the user.

    in_class: A flag for if the user is in the class. Options:
        - in_class: The user is in the class.
        - not_in_class: The user is not in the class.
    """

    def _retrieve_class(
        self,
        klass: Class,
        status_code_assertion: APIClient.StatusCodeAssertion = None,
    ):
        return self.client.retrieve(
            "class",
            klass,
            ClassSerializer,
            status_code_assertion,
            ClassViewSet,
        )

    def test_retrieve__student__same_school__in_class(self):
        """
        Student can retrieve a class from the same school and a class they are
        in.
        """

        user = self._login_student()

        self._retrieve_class(user.student.class_field)

    # TODO: other retrieve and list tests
    # TODO: fix unit tests.
