from rest_framework import serializers

from ..models import User
from .student import StudentSerializer
from .teacher import TeacherSerializer


class UserSerializer(serializers.ModelSerializer):
    student = StudentSerializer(source="new_student", read_only=True)
    teacher = TeacherSerializer(source="new_teacher", read_only=True)

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
        }
