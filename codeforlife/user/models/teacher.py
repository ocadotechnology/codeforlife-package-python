"""
© Ocado Group
Created on 05/02/2024 at 09:49:56(+00:00).
"""

from common.models import Teacher
from django_stubs_ext.db.models import TypedModelMeta

from .school import School


class SchoolTeacher(Teacher):
    """A teacher that is in a school."""

    school: School

    class Meta(TypedModelMeta):
        proxy = True


class NonSchoolTeacher(Teacher):
    """A teacher that is not in a school."""

    school: None

    class Meta(TypedModelMeta):
        proxy = True
