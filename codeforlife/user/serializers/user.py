from rest_framework import serializers

from ..models import User
from .student import StudentSerializer
from .teacher import TeacherSerializer


class UserSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    teacher = TeacherSerializer()

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True},
        }
