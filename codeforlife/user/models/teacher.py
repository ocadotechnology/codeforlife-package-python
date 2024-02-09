"""
© Ocado Group
Created on 05/02/2024 at 09:49:56(+00:00).
"""

import typing as t

from common.models import Teacher, TeacherModelManager
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta

from .school import School


class SchoolTeacher(Teacher):
    """A teacher that is in a school."""

    school: School

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(TeacherModelManager):
        def get_queryset(self):
            return super().get_queryset().filter(school__isnull=False)

    objects: models.Manager["SchoolTeacher"] = Manager()


class AdminSchoolTeacher(SchoolTeacher):
    """An admin-teacher that is in a school."""

    is_admin: t.Literal[True]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(SchoolTeacher.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_admin=True)

    objects: models.Manager["AdminSchoolTeacher"] = Manager()


class NonAdminSchoolTeacher(SchoolTeacher):
    """A non-admin-teacher that is in a school."""

    is_admin: t.Literal[False]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(SchoolTeacher.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_admin=False)

    objects: models.Manager["NonAdminSchoolTeacher"] = Manager()


class NonSchoolTeacher(Teacher):
    """A teacher that is not in a school."""

    school: None

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(TeacherModelManager):
        def get_queryset(self):
            return super().get_queryset().filter(school__isnull=True)

    objects: models.Manager["NonSchoolTeacher"] = Manager()
