"""
© Ocado Group
Created on 05/12/2023 at 17:44:05(+00:00).

School model.
"""

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

from ...models import WarehouseModel
from ...models.fields import Country, UkCounty
from . import klass as _class
from . import student as _student
from . import teacher as _teacher


class School(WarehouseModel):
    """A collection of teachers and students."""

    # pylint: disable-next=missing-class-docstring
    class Manager(WarehouseModel.Manager["School"]):
        pass

    objects: Manager = Manager()

    teachers: QuerySet["_teacher.Teacher"]
    students: QuerySet["_student.Student"]
    classes: QuerySet["_class.Class"]

    name = models.CharField(
        _("name"),
        max_length=200,
        unique=True,
        help_text=_("The school's name."),
    )

    country = models.TextField(
        _("country"),
        choices=Country.choices,
        null=True,
        blank=True,
        help_text=_("The school's country."),
    )

    uk_county = models.TextField(
        _("united kingdom county"),
        choices=UkCounty.choices,
        null=True,
        blank=True,
        help_text=_(
            "The school's county within the United Kingdom. This value may only"
            " be set if the school's country is set to UK."
        ),
    )

    class Meta(TypedModelMeta):
        verbose_name = _("school")
        verbose_name_plural = _("schools")
        constraints = [
            models.CheckConstraint(
                check=Q(uk_county__isnull=True) | Q(country="UK"),
                name="school__no_uk_county_if_country_not_uk",
            ),
        ]
