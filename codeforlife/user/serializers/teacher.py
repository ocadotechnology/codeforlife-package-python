from rest_framework import serializers

from ..models import Teacher


# pylint: disable-next=missing-class-docstring
class TeacherSerializer(serializers.ModelSerializer[Teacher]):
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
        }
