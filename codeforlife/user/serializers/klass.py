from rest_framework import serializers

from ..models import Class


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
        }
