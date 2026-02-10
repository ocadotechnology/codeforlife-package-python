"""
© Ocado Group
Created on 20/02/2024 at 15:37:52(+00:00).
"""

from uuid import uuid4

from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField

from ...types import Validators
from ...validators import UnicodeAlphanumericCharSetValidator

# TODO: add to School.name field-validators in new schema.
school_name_validators: Validators = [
    UnicodeAlphanumericCharSetValidator(
        spaces=True,
        special_chars="'.",
    )
]


class SchoolModelManager(models.Manager):
    def get_original_queryset(self):
        return super().get_queryset()

    # Filter out inactive schools by default
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class School(models.Model):
    name = models.CharField(max_length=200, unique=True)
    country = CountryField(
        blank_label="(select country)", null=True, blank=True
    )
    # TODO: Create an Address model to house address details
    county = models.CharField(max_length=50, blank=True, null=True)
    creation_time = models.DateTimeField(default=timezone.now, null=True)
    is_active = models.BooleanField(default=True)

    objects = SchoolModelManager()

    def __str__(self):
        return self.name

    def classes(self):
        teachers = self.teacher_school.all()
        if teachers:
            classes = []
            for teacher in teachers:
                if teacher.class_teacher.all():
                    classes.extend(list(teacher.class_teacher.all()))
            return classes
        return None

    def admins(self):
        teachers = self.teacher_school.all()
        return (
            [teacher for teacher in teachers if teacher.is_admin]
            if teachers
            else None
        )

    def anonymise(self):
        self.name = uuid4().hex
        self.is_active = False
        self.save()
