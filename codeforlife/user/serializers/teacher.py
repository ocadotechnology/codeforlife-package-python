"""
© Ocado Group
Created on 20/01/2024 at 11:27:43(+00:00).
"""

from ...serializers import ModelSerializer
from ..models import Teacher


# pylint: disable-next=missing-class-docstring
class TeacherSerializer(ModelSerializer[Teacher]):
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
