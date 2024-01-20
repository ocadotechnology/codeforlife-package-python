"""
© Ocado Group
Created on 20/01/2024 at 09:48:30(+00:00).
"""

from ....tests import ModelViewSetTestCase
from ...models import Class
from ...serializers import ClassSerializer
from ...views import ClassViewSet


class TestClassViewSet(
    ModelViewSetTestCase[ClassViewSet, ClassSerializer, Class]
):
    """
    Base naming convention:
        test_{action}

    action: The view set action.
        https://www.django-rest-framework.org/api-guide/viewsets/#viewset-actions
    """

    basename = "class"

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

    def test_retrieve__student__same_school__in_class(self):
        """
        Student can retrieve a class from the same school and a class they are
        in.
        """

        user = self._login_student()

        self.client.retrieve(user.student.class_field)

    # TODO: other retrieve and list tests
