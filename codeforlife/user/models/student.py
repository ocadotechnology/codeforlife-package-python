"""
© Ocado Group
Created on 05/12/2023 at 17:43:33(+00:00).

Student model.
"""

import typing as t

from django.contrib.auth.hashers import make_password
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from ...models import AbstractModel
from . import class_student_join_request as _class_student_join_request
from . import klass as _class
from . import school as _school
from . import user as _user


class Student(AbstractModel):
    """A user's student profile."""

    class Manager(models.Manager):  # pylint: disable=missing-class-docstring
        def create(self, direct_login_key: str, **fields):
            return super().create(
                **fields,
                direct_login_key=make_password(direct_login_key),
            )

        def bulk_create(self, students: t.Iterable["Student"], *args, **kwargs):
            for student in students:
                student.direct_login_key = make_password(
                    student.direct_login_key
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
            students = [student for (student, _) in student_users]
            users = [user for (_, user) in student_users]

            students = self.bulk_create(students, *args, **kwargs)

            for student, user in zip(students, users):
                user.student = student

            return _user.User.objects.bulk_create(users, *args, **kwargs)

        def make_random_direct_login_key(self):
            return _user.User.objects.make_random_password(
                length=Student.direct_login_key.max_length
            )

    objects: Manager = Manager()

    user: "_user.User"
    class_join_requests: QuerySet[
        "_class_student_join_request.ClassStudentJoinRequest"
    ]

    # Is this needed or can it be inferred from klass.
    school: "_school.School" = models.ForeignKey(
        "user.School",
        related_name="students",
        null=True,
        editable=False,
        on_delete=models.CASCADE,
    )

    klass: "_class.Class" = models.ForeignKey(
        "user.Class",
        related_name="students",
        null=True,
        editable=False,
        on_delete=models.CASCADE,
    )

    second_password = models.CharField(  # TODO: make nullable
        _("secondary password"),
        max_length=64,  # investigate hash length
        editable=False,
        help_text=_(
            "A unique key that allows a student to log directly into their"
            "account."  # TODO
        ),
        validators=[MinLengthValidator(64)],
    )

    # TODO: add direct reference to teacher
    # TODO: add meta constraint for school & direct_login_key

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(school__isnull=True, klass__isnull=True)
                    | Q(school__isnull=False, klass__isnull=False)
                ),
                name="student__school_is_null_and_class_is_null",
            ),
        ]
