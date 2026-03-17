"""
© Ocado Group
Created on 20/02/2024 at 15:37:52(+00:00).
"""

import typing as t
from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from ...models import DataEncryptionKeyModel
from ...models.fields import EncryptedTextField
from ...types import Validators
from ...validators import UnicodeAlphanumericCharSetValidator

if t.TYPE_CHECKING:  # pragma: no cover
    from datetime import datetime


# TODO: add to School.name field-validators in new schema.
school_name_validators: Validators = [
    UnicodeAlphanumericCharSetValidator(
        spaces=True,
        special_chars="'.",
    )
]


class SchoolModelManager(DataEncryptionKeyModel.Manager["School"]):
    """Manager for School model."""

    def get_original_queryset(self):
        """Get the original queryset without filtering."""
        return super().get_queryset()

    def get_queryset(self):
        """Filter out inactive schools by default."""
        return super().get_queryset().filter(is_active=True)


class School(DataEncryptionKeyModel):
    """A school."""

    associated_data = "school"

    name = EncryptedTextField(
        associated_data="name",
        null=True,
        verbose_name=_("name"),
    )

    country: t.Optional[str]
    country = CountryField(  # type: ignore[assignment]
        blank_label="(select country)",
        null=True,
        blank=True,
    )

    # TODO: Create an Address model to house address details
    county: t.Optional[str]
    county = models.CharField(  # type: ignore[assignment]
        max_length=50,
        blank=True,
        null=True,
    )

    creation_time: t.Optional["datetime"]
    creation_time = models.DateTimeField(  # type: ignore[assignment]
        default=timezone.now,
        null=True,
    )

    is_active: bool
    is_active = models.BooleanField(default=True)  # type: ignore[assignment]

    objects: SchoolModelManager = (
        SchoolModelManager()  # type: ignore[assignment]
    )

    def __str__(self):
        return self.name

    def classes(self):
        """Get all classes associated with the school."""
        teachers = self.teacher_school.all()
        if teachers:
            classes = []
            for teacher in teachers:
                if teacher.class_teacher.all():
                    classes.extend(list(teacher.class_teacher.all()))
            return classes
        return None

    def admins(self):
        """Get all admin teachers associated with the school."""
        teachers = self.teacher_school.all()
        return (
            [teacher for teacher in teachers if teacher.is_admin]
            if teachers
            else None
        )

    def anonymise(self):
        """Anonymize the school."""
        self.name = uuid4().hex
        self.is_active = False
        self.save()
