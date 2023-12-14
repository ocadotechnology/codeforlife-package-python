"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from rest_framework.views import APIView

from ....tests import APITestCase
from ...permissions import InClass


class TestInClass(APITestCase):
    """
    Naming convention:
        test_{class_id}__{user_type}

    class_id: The id of a class. Options:
        - any_class: Any class.
        - in_class: A specific class the user is in.
        - not_in_class: A specific class the user is not in.

    user_type: The type of user. Options:
        - non_class_teacher: A teacher not in a class.
        - class_teacher: A teacher in a class.
        - student: A student.
        - indy: An independent.
    """

    def test_any_class__non_class_teacher(self):
        """
        Teacher without a class is not in any class.
        """

        raise NotImplementedError()  # TODO

    def test_any_class__class_teacher(self):
        """
        Teacher with a class is in any class.
        """

        raise NotImplementedError()  # TODO

    def test_any_class__student(self):
        """
        Student is in any class.
        """

        raise NotImplementedError()  # TODO

    def test_any_class__indy(self):
        """
        Independent is not in any class.
        """

        raise NotImplementedError()  # TODO

    def test_not_in_class__non_class_teacher(self):
        """
        Teacher without a class is not in a specific class.
        """

        raise NotImplementedError()  # TODO

    def test_not_in_class__class_teacher(self):
        """
        Teacher with a class is not in a specific class.
        """

        raise NotImplementedError()  # TODO

    def test_not_in_class__student(self):
        """
        Student is not in a specific class.
        """

        raise NotImplementedError()  # TODO

    def test_not_in_class__indy(self):
        """
        Independent is not in a specific class.
        """

        raise NotImplementedError()  # TODO

    def test_in_class__class_teacher(self):
        """
        Teacher with a class is in a specific class.
        """

        raise NotImplementedError()  # TODO

    def test_in_class__student(self):
        """
        Student is in a specific class.
        """

        raise NotImplementedError()  # TODO
