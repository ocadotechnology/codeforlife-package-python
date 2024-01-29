"""
© Ocado Group
Created on 20/01/2024 at 11:27:56(+00:00).
"""

from rest_framework import serializers

from ...serializers import ModelSerializer
from ..models import Student


# pylint: disable-next=missing-class-docstring
class StudentSerializer(ModelSerializer[Student]):
    klass = serializers.CharField(source="class_field.access_code")

    school = serializers.IntegerField(source="class_field.teacher.school.id")

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
            "klass": {"read_only": True},
            "school": {"read_only": True},
        }
