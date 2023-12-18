"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from rest_framework.views import APIView

from ....tests import APITestCase
from ...permissions import IsIndependent


class TestIsIndependent(APITestCase):
    """
    Naming convention:
        test_{user_type}

    user_type: The type of user. Options:
        - teacher: A teacher.
        - student: A student.
        - indy: An independent.
    """

    def test_teacher(self):
        """
        Teacher is not any independent.
        """

        raise NotImplementedError()  # TODO

    def test_student(self):
        """
        Student is not any independent.
        """

        raise NotImplementedError()  # TODO

    def test_indy(self):
        """
        Independent is any independent.
        """

        raise NotImplementedError()  # TODO
