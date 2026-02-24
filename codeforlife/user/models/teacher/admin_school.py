"""
© Ocado Group
Created on 19/02/2024 at 21:54:04(+00:00).
"""

import typing as t

from django.db import models

from .school import SchoolTeacher

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


class AdminSchoolTeacher(SchoolTeacher):
    """An admin-teacher that is in a school."""

    is_admin: t.Literal[True]  # type: ignore[assignment]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(SchoolTeacher.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_admin=True)

    # pylint: disable-next=line-too-long
    objects: models.Manager["AdminSchoolTeacher"] = Manager()  # type: ignore[misc]

    @property
    def is_last_admin(self):
        """Whether of not the teacher is the last admin in the school."""
        return (
            not self.__class__.objects.filter(school=self.school)
            .exclude(pk=self.pk)
            .exists()
        )
