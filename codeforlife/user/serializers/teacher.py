"""
© Ocado Group
Created on 20/01/2024 at 11:27:43(+00:00).
"""

import typing as t

from ...serializers import ModelSerializer
from ..models import AnyTeacher, Teacher


# pylint: disable-next=missing-class-docstring
class BaseTeacherSerializer(ModelSerializer[AnyTeacher], t.Generic[AnyTeacher]):
    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta:
        model = Teacher
        fields = [
            "id",
            "school",
            "is_admin",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "school": {"read_only": True},
            "is_admin": {"read_only": True},
        }


# pylint: disable-next=missing-class-docstring,too-many-ancestors
class TeacherSerializer(BaseTeacherSerializer[Teacher]):
    pass
