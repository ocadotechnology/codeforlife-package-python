"""
© Ocado Group
Created on 05/12/2023 at 17:44:48(+00:00).

Class model.

NOTE: This module has been named "klass" as "class" is a reserved keyword.
"""

from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

from ...models import WarehouseModel
from . import school as _school
from . import student as _student
from . import teacher as _teacher


class Class(WarehouseModel):
    """A collection of students owned by a teacher."""

    # pylint: disable-next=missing-class-docstring
    class Manager(WarehouseModel.Manager["Class"]):
        pass

    objects: Manager = Manager()

    pk: str  # type: ignore[assignment]
    students: QuerySet["_student.Student"]

    id: str = models.CharField(  # type: ignore[assignment]
        _("identifier"),
        primary_key=True,
        editable=False,
        max_length=5,
        help_text=_("Uniquely identifies a class."),
        validators=[
            MinLengthValidator(5),
            RegexValidator(
                regex=r"^[0-9A-Z]*$",
                message="ID must be alphanumeric with upper case characters.",
                code="id_not_upper_alphanumeric",
            ),
        ],
    )

    teacher_id: int
    teacher: "_teacher.Teacher" = models.ForeignKey(  # type: ignore[assignment]
        "user.Teacher",
        related_name="classes",
        on_delete=models.CASCADE,
    )

    school_id: int
    school: "_school.School" = models.ForeignKey(  # type: ignore[assignment]
        "user.School",
        related_name="classes",
        on_delete=models.CASCADE,
    )

    name = models.CharField(
        _("name"),
        max_length=200,
    )

    # TODO: phase out and use django's permission system.
    read_classmates_data = models.BooleanField(
        _("read classmates data"),
        default=False,
        help_text=_(
            "Designates whether students in this class can see their fellow"
            " classmates' data."
        ),
    )

    receive_requests_until = models.DateTimeField(
        _("accept student join requests until"),
        null=True,
        help_text=_(
            "A point in the future until which the class can receive requests"
            " from students to join. Set to null if it's not accepting"
            " requests."
        ),
    )

    class Meta(TypedModelMeta):
        verbose_name = _("class")
        verbose_name_plural = _("classes")
        unique_together = ["name", "school"]
