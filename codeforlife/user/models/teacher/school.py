"""
© Ocado Group
Created on 19/02/2024 at 21:54:04(+00:00).
"""

import typing as t

from django.db import models
from django.db.models import Q

from .teacher import Teacher, TeacherModelManager

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta

    from ..school import School
else:
    TypedModelMeta = object


class SchoolTeacher(Teacher):
    """A teacher that is in a school."""

    school: "School"  # type: ignore[assignment]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(TeacherModelManager):
        def get_queryset(self):
            return super().get_queryset().filter(school__isnull=False)

    # pylint: disable-next=line-too-long
    objects: models.Manager["SchoolTeacher"] = Manager()  # type: ignore[assignment,misc]

    @property
    def student_users(self):
        """All student-users the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from ..user.student import StudentUser

        return StudentUser.objects.filter(
            **(
                {"new_student__class_field__teacher__school": self.school}
                if self.is_admin
                else {"new_student__class_field__teacher": self}
            )
        ).prefetch_related("new_student")

    @property
    def students(self):
        """All students the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from ..student import Student

        return Student.objects.filter(
            **(
                {"class_field__teacher__school": self.school}
                if self.is_admin
                else {"class_field__teacher": self}
            )
        ).prefetch_related("new_user")

    @property
    def classes(self):
        """All classes the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from ..klass import Class

        return Class.objects.filter(teacher__school=self.school)

    @property
    def indy_users(self):
        """All independent-users the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from ..user.independent import IndependentUser

        return IndependentUser.objects.filter(
            new_student__pending_class_request__in=self.classes
        )

    @property
    def school_teacher_users(self):
        """All school-teacher-users the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from ..user.school_teacher import SchoolTeacherUser

        return SchoolTeacherUser.objects.filter(new_teacher__school=self.school)

    @property
    def school_teachers(self):
        """All school-teachers the teacher can query."""
        return SchoolTeacher.objects.filter(school=self.school)

    @property
    def school_users(self):
        """All users in the school the teacher can query."""
        # pylint: disable-next=import-outside-toplevel
        from ..user.user import User

        return User.objects.filter(
            Q(  # student-users
                new_teacher__isnull=True,
                **(
                    {"new_student__class_field__teacher__school": self.school}
                    if self.is_admin
                    else {"new_student__class_field__teacher": self}
                ),
            )
            | Q(  # school-teacher-users
                new_student__isnull=True,
                new_teacher__school=self.school,
            )
        )
