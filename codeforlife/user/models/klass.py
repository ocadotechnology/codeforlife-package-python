"""
© Ocado Group
Created on 05/12/2023 at 17:44:48(+00:00).

Class model.

NOTE: This module has been named "klass" as "class" is a reserved keyword.
"""

from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _

from ...models import AbstractModel
from . import class_student_join_request as _class_student_join_request
from . import school as _school
from . import student as _student
from . import teacher as _teacher


class Class(AbstractModel):
    """A collection of students owned by a teacher."""

    pk: str  # type: ignore
    students: QuerySet["_student.Student"]
    student_join_requests: QuerySet[
        "_class_student_join_request.ClassStudentJoinRequest"
    ]

    id = models.CharField(
        _("identifier"),
        primary_key=True,
        editable=False,
        max_length=5,
        help_text=_("Uniquely identifies a class."),
        validators=[
            MinLengthValidator(5),
            RegexValidator(
                regex=r"^[0-9a-zA-Z]*$",
                message="ID must be alphanumeric.",
                code="id_not_alphanumeric",
            ),
        ],
    )

    teacher: "_teacher.Teacher" = models.ForeignKey(
        "user.Teacher",
        related_name="classes",
        on_delete=models.CASCADE,
    )

    school: "_school.School" = models.ForeignKey(
        "user.School",
        related_name="classes",
        on_delete=models.CASCADE,
    )

    read_classmates_data = models.BooleanField(
        _("read classmates data"),
        default=False,
        help_text=_(
            "Designates whether students in this class can see their fellow"
            " classmates' data."
        ),
    )

    accept_requests_until = models.DateTimeField(
        _("accept student join requests until"),
        null=True,
        blank=True,
        help_text=_(
            "A point in the future until which requests from students to join"
            " this class are accepted. Set to null if it's not accepting"
            " requests."
        ),
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(teacher__school=F("school")),
                name="class__teacher_in_school",
            ),
        ]
