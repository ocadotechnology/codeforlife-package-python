"""
© Ocado Group
Created on 20/01/2024 at 11:28:19(+00:00).
"""

from rest_framework import serializers

from ...serializers import ModelSerializer
from ..models import School


# pylint: disable-next=missing-class-docstring
class SchoolSerializer(ModelSerializer[School]):
    uk_county = serializers.CharField(source="county")

    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "country",
            "uk_county",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "name": {"read_only": True},
            "country": {"read_only": True},
            "uk_county": {"read_only": True},
        }
