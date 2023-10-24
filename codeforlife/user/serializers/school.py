from rest_framework import serializers

from ..models import School


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "creation_time": {"read_only": True},
        }
