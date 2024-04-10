"""
© Ocado Group
Created on 20/01/2024 at 11:27:43(+00:00).
"""

import typing as t

from ...serializers import ModelSerializer
from ..models import AnyTeacher, Teacher
from ..models import User as RequestUser

# pylint: disable=missing-class-docstring
# pylint: disable=too-many-ancestors


class TeacherSerializer(
    ModelSerializer[RequestUser, AnyTeacher], t.Generic[AnyTeacher]
):
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
