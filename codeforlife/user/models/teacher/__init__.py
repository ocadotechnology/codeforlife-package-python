"""
© Ocado Group
Created on 19/02/2024 at 21:54:04(+00:00).
"""

import typing as t

from .admin_school import AdminSchoolTeacher
from .non_admin_school import NonAdminSchoolTeacher
from .non_school import NonSchoolTeacher
from .school import SchoolTeacher
from .teacher import AnyTeacher, Teacher

# pylint: disable-next=invalid-name
TypedTeacher = t.Union[
    SchoolTeacher,
    AdminSchoolTeacher,
    NonAdminSchoolTeacher,
    NonSchoolTeacher,
]

AnyTypedTeacher = t.TypeVar("AnyTypedTeacher", bound=TypedTeacher)


# TODO: add this as a method on base Teacher model in new schema.
def teacher_as_type(
    teacher: Teacher, typed_teacher_class: t.Type[AnyTypedTeacher]
):
    """Convert a generic teacher to a typed teacher.

    Args:
        teacher: The teacher to convert.
        typed_teacher_class: The type of teacher to convert to.

    Returns:
        An instance of the typed teacher.
    """

    return typed_teacher_class(
        pk=teacher.pk,
        user=teacher.user,
        new_user=teacher.new_user,
        school=teacher.school,
        is_admin=teacher.is_admin,
        blocked_time=teacher.blocked_time,
        invited_by=teacher.invited_by,
    )
