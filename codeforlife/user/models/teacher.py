"""
© Ocado Group
Created on 05/02/2024 at 09:49:56(+00:00).
"""

import typing as t

from common.models import Teacher, TeacherModelManager
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta

from .school import School
from .student import Student


class SchoolTeacher(Teacher):
    """A teacher that is in a school."""

    school: School

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(TeacherModelManager):
        def get_queryset(self):
            return super().get_queryset().filter(school__isnull=False)

    objects: models.Manager["SchoolTeacher"] = Manager()

    @property
    def student_users(self):
        """All student-users the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from .user import StudentUser

        return StudentUser.objects.filter(
            **(
                {"new_student__class_field__teacher__school": self.school}
                if self.is_admin
                else {"new_student__class_field__teacher": self}
            )
        )

    @property
    def students(self):
        """All students the teacher can query."""
        return Student.objects.filter(
            **(
                {"class_field__teacher__school": self.school}
                if self.is_admin
                else {"class_field__teacher": self}
            )
        )


class AdminSchoolTeacher(SchoolTeacher):
    """An admin-teacher that is in a school."""

    is_admin: t.Literal[True]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(SchoolTeacher.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_admin=True)

    objects: models.Manager["AdminSchoolTeacher"] = Manager()


class NonAdminSchoolTeacher(SchoolTeacher):
    """A non-admin-teacher that is in a school."""

    is_admin: t.Literal[False]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(SchoolTeacher.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_admin=False)

    objects: models.Manager["NonAdminSchoolTeacher"] = Manager()


class NonSchoolTeacher(Teacher):
    """A teacher that is not in a school."""

    school: None

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(TeacherModelManager):
        def get_queryset(self):
            return super().get_queryset().filter(school__isnull=True)

    objects: models.Manager["NonSchoolTeacher"] = Manager()


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
