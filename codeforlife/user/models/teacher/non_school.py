"""
© Ocado Group
Created on 19/02/2024 at 21:54:04(+00:00).
"""

import typing as t

from django.db import models

from .teacher import Teacher, TeacherModelManager

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


class NonSchoolTeacher(Teacher):
    """A teacher that is not in a school."""

    school: None  # type: ignore[assignment]
    is_admin: t.Literal[False]  # type: ignore[assignment]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(TeacherModelManager):
        def get_queryset(self):
            return super().get_queryset().filter(school__isnull=True)

    # pylint: disable-next=line-too-long
    objects: models.Manager["NonSchoolTeacher"] = Manager()  # type: ignore[assignment,misc]
