"""
© Ocado Group
Created on 05/12/2023 at 17:43:33(+00:00).

Student model.
"""

import typing as t

from django.contrib.auth.hashers import make_password
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

from ...models import WarehouseModel
from . import klass as _class
from . import school as _school
from . import user as _user


class Student(WarehouseModel):
    """A user's student profile."""

    # pylint: disable-next=missing-class-docstring
    class Manager(WarehouseModel.Manager["Student"]):
        def create(  # type: ignore[override]
            self,
            auto_gen_password: str,
            **fields,
        ):
            """Create a student.

            Args:
                auto_gen_password: The student's auto-generated password.

            Returns:
                A student instance.
            """

            return super().create(
                **fields,
                auto_gen_password=make_password(auto_gen_password),
            )

        def bulk_create(  # type: ignore[override]
            self,
            students: t.Iterable["Student"],
            *args,
            **kwargs,
        ):
            """Bulk create students.

            Args:
                students: An iteration of student objects.

            Returns:
                A list of student instances.
            """

            for student in students:
                student.auto_gen_password = make_password(
                    student.auto_gen_password
                )

            return super().bulk_create(students, *args, **kwargs)

        def create_user(self, student: t.Dict[str, t.Any], **fields):
            """Create a user with a student profile.

            Args:
                user: The user fields.

            Returns:
                A student profile.
            """

            return _user.User.objects.create_user(
                **fields,
                student=self.create(**student),
            )

        def bulk_create_users(
            self,
            student_users: t.List[t.Tuple["Student", "_user.User"]],
            *args,
            **kwargs,
        ):
            """Bulk create users with student profiles.

            Args:
                student_users: A list of tuples where the first object is the
                    student profile and the second is the user whom the student
                    profile belongs to.

            Returns:
                A list of users that have been assigned their student profile.
            """

            students = [student for (student, _) in student_users]
            users = [user for (_, user) in student_users]

            students = self.bulk_create(students, *args, **kwargs)

            for student, user in zip(students, users):
                user.student = student

            return _user.User.objects.bulk_create(users, *args, **kwargs)

    objects: Manager = Manager()

    user: "_user.User"

    school_id: int
    school: "_school.School" = models.ForeignKey(  # type: ignore[assignment]
        "user.School",
        related_name="students",
        editable=False,
        on_delete=models.CASCADE,
    )

    klass_id: str
    klass: "_class.Class" = models.ForeignKey(  # type: ignore[assignment]
        "user.Class",
        related_name="students",
        on_delete=models.CASCADE,
    )

    auto_gen_password = models.CharField(
        _("automatically generated password"),
        max_length=64,
        editable=False,
        help_text=_(
            "An auto-generated password that allows student to log directly"
            " into their account."
        ),
        validators=[MinLengthValidator(64)],
    )

    class Meta(TypedModelMeta):
        verbose_name = _("student")
        verbose_name_plural = _("students")

    @property
    def teacher(self):
        """The student's teacher (if they have one).

        Returns:
            The student's class-teacher.
        """

        return self.klass.teacher
