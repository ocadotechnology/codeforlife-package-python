from uuid import uuid4

from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField


class SchoolModelManager(models.Manager):
    # Filter out inactive schools by default
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class School(models.Model):
    name = models.CharField(max_length=200)
    postcode = models.CharField(max_length=10, null=True)
    country = CountryField(blank_label="(select country)")
    creation_time = models.DateTimeField(default=timezone.now, null=True)
    is_active = models.BooleanField(default=True)

    objects = SchoolModelManager()

    def __str__(self):
        return self.name

    def classes(self):
        teachers = self.school_teacher.all()
        if teachers:
            classes = []
            for teacher in teachers:
                if teacher.class_teacher.all():
                    classes.extend(list(teacher.class_teacher.all()))
            return classes
        return None

    def admins(self):
        teachers = self.school_teacher.all()
        return (
            [teacher for teacher in teachers if teacher.is_admin]
            if teachers
            else None
        )

    def anonymise(self):
        self.name = uuid4().hex
        self.postcode = ""
        self.is_active = False
        self.save()
