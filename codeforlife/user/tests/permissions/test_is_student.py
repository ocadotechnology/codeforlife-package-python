"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from ....tests import PermissionTestCase
from ...permissions import IsStudent


class TestIsStudent(PermissionTestCase[IsStudent]):
    """
    Naming convention:
        test_{user_type}__{student_id}

    user_type: The type of user. Options:
        - teacher: A teacher.
        - student: A student.
        - indy: An independent.

    student_id: The ID of a student. Options:
        - any_student: User is any student.
        - not_any_student: User is not any student.
        - specific_student: User is a specific student.
        - not_specific_student User is not a specific student.
    """

    def test_teacher__not_any_student(self):
        """
        Teacher is not any student.
        """

        raise NotImplementedError()  # TODO

    def test_teacher__not_specific_student(self):
        """
        Teacher is not a specific student.
        """

        raise NotImplementedError()  # TODO

    def test_indy__not_any_student(self):
        """
        Independent is not any student.
        """

        raise NotImplementedError()  # TODO

    def test_indy__not_specific_student(self):
        """
        Independent is not a specific student.
        """

        raise NotImplementedError()  # TODO

    def test_student__any_student(self):
        """
        Student is any student.
        """

        raise NotImplementedError()  # TODO

    def test_student__specific_student(self):
        """
        Student is a specific student.
        """

        raise NotImplementedError()  # TODO

    def test_student__not_specific_student(self):
        """
        Student is not a specific student.
        """

        raise NotImplementedError()  # TODO
