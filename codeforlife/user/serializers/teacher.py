from rest_framework import serializers

from ..models import Teacher


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
        }
