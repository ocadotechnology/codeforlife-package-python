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


class NonAdminSchoolTeacher(SchoolTeacher):
    """A non-admin-teacher that is in a school."""

    is_admin: t.Literal[False]  # type: ignore[assignment]

    class Meta(TypedModelMeta):
        proxy = True

    # pylint: disable-next=missing-class-docstring
    class Manager(SchoolTeacher.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_admin=False)

    # pylint: disable-next=line-too-long
    objects: models.Manager["NonAdminSchoolTeacher"] = Manager()  # type: ignore[misc]
