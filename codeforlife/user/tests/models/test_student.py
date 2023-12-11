"""
© Ocado Group
Created on 08/12/2023 at 17:43:11(+00:00).
"""

from ....tests import ModelTestCase
from ...models import Student


class TestStudent(ModelTestCase[Student]):
    """Tests the Student model."""

    # TODO: test docstrings.

    def test_objects__create(self):
        """
        Create a student.
        """

        raise NotImplementedError()  # TODO

    def test_objects__bulk_create(self):
        """
        Bulk create many students.
        """

        raise NotImplementedError()  # TODO

    def test_objects__create_user(self):
        """
        Create a user with a student profile.
        """

        raise NotImplementedError()  # TODO

    def test_objects__bulk_create_users(self):
        """
        Bulk create many users with a student profile.
        """

        raise NotImplementedError()  # TODO

    def test_teacher(self):
        """
        Get student's teacher.
        """

        raise NotImplementedError()  # TODO
