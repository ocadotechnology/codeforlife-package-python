"""
© Ocado Group
Created on 20/01/2024 at 11:27:56(+00:00).
"""

from ...serializers import ModelSerializer
from ..models import Student


# pylint: disable-next=missing-class-docstring
class StudentSerializer(ModelSerializer[Student]):
    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta:
        model = Student
        fields = [
            "id",
            "klass",
            "school",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "klass": instance.class_field.access_code,
            "school": instance.class_field.teacher.school.pk,
        }
