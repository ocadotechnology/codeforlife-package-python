"""
© Ocado Group
Created on 20/01/2024 at 11:27:56(+00:00).
"""

from rest_framework import serializers

from ...serializers import ModelSerializer
from ..models import Student
from ..models import User as RequestUser

# pylint: disable=missing-class-docstring
# pylint: disable=too-many-ancestors


class StudentSerializer(ModelSerializer[RequestUser, Student]):
    klass = serializers.CharField(
        source="class_field.access_code", read_only=True
    )

    school = serializers.IntegerField(
        source="class_field.teacher.school.id", read_only=True
    )

    class Meta:
        model = Student
        fields = ["id", "klass", "school"]
        extra_kwargs = {"id": {"read_only": True}}
