"""
© Ocado Group
Created on 20/01/2024 at 11:28:29(+00:00).
"""

from rest_framework import serializers

from ...serializers import ModelSerializer
from ..models import Class


# pylint: disable-next=missing-class-docstring
class ClassSerializer(ModelSerializer[Class]):
    id = serializers.CharField(
        source="access_code",
        read_only=True,
    )

    read_classmates_data = serializers.BooleanField(
        source="classmates_data_viewable",
        read_only=True,
    )

    receive_requests_until = serializers.DateTimeField(
        source="accept_requests_until",
        read_only=True,
    )

    teacher = serializers.IntegerField(
        source="teacher.id",
        read_only=True,
    )

    school = serializers.IntegerField(
        source="teacher.school.id",
        read_only=True,
    )

    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta:
        model = Class
        fields = [
            "id",
            "teacher",
            "school",
            "name",
            "read_classmates_data",
            "receive_requests_until",
        ]
        extra_kwargs = {
            "name": {"read_only": True},
        }
