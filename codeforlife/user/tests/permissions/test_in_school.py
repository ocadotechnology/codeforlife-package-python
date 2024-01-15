"""
© Ocado Group
Created on 14/12/2023 at 14:26:20(+00:00).
"""

from ....tests import PermissionTestCase
from ...permissions import InSchool


class TestInSchool(PermissionTestCase[InSchool]):
    """
    Naming convention:
        test_{school_id}__{user_type}

    school_id: The id of a school. Options:
        - any_school: Any school.
        - in_school: A specific school the user is in.
        - not_in_school: A specific school the user is not in.

    user_type: The type of user. Options:
        - non_school_teacher: A teacher not in a school.
        - school_teacher: A teacher in a school.
        - student: A student.
        - indy: An independent.
    """

    # TODO: define unit tests
