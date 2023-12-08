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
from django_stubs_ext.db.models import TypedModelMeta

from ...models import AbstractModel
from . import class_student_join_request as _class_student_join_request
from . import klass as _class
from . import school as _school
from . import user as _user


class Student(AbstractModel):
    """A user's student profile."""

    # pylint: disable-next=missing-class-docstring
    class Manager(models.Manager["Student"]):
        def create(  # type: ignore[override]
            self,
            auto_gen_password: t.Optional[str] = None,
            **fields,
        ):
            """Create a student.

            Args:
                auto_gen_password: The student's auto-generated password.

            Returns:
                A student instance.
            """

            if auto_gen_password:
                auto_gen_password = make_password(auto_gen_password)

            return super().create(**fields, auto_gen_password=auto_gen_password)

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
                if student.auto_gen_password:
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

    objects: Manager = Manager.from_queryset(  # type: ignore[misc]
        AbstractModel.QuerySet
    )()  # type: ignore[assignment]

    user: "_user.User"
    # class_join_requests: QuerySet[
    #     "_class_student_join_request.ClassStudentJoinRequest"
    # ]

    # Is this needed or can it be inferred from klass.
    # school: "_school.School" = models.ForeignKey(
    #     "user.School",
    #     related_name="students",
    #     null=True,
    #     editable=False,
    #     on_delete=models.CASCADE,
    # )

    # klass: "_class.Class" = models.ForeignKey(
    #     "user.Class",
    #     related_name="students",
    #     null=True,
    #     editable=False,
    #     on_delete=models.CASCADE,
    # )

    auto_gen_password = models.CharField(
        _("automatically generated password"),
        max_length=64,
        editable=False,
        null=True,
        help_text=_(
            "An auto-generated password that allows student to log directly"
            " into their account."
        ),
        validators=[MinLengthValidator(64)],
    )

    # TODO: add direct reference to teacher

    class Meta(TypedModelMeta):
        verbose_name = _("student")
        verbose_name_plural = _("students")
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(school__isnull=True, klass__isnull=True)
                    | Q(school__isnull=False, klass__isnull=False)
                ),
                name="student__school_and_klass",
            ),
            models.CheckConstraint(
                check=(
                    Q(school__isnull=False, auto_gen_password__isnull=False)
                    | Q(school__isnull=True, auto_gen_password__isnull=True)
                ),
                name="student__auto_gen_password",
            ),
        ]
