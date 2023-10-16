from rest_framework import serializers

from ..models import User
from .student import StudentSerializer
from .teacher import TeacherSerializer


class UserSerializer(serializers.ModelSerializer):
    student = StudentSerializer(source="new_student", read_only=True)
    teacher = TeacherSerializer(source="new_teacher", read_only=True)
    current_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "username": {"read_only": True},
            "isActive": {"read_only": True},
            "isStaff": {"read_only": True},
            "dateJoined": {"read_only": True},
            "lastLogin": {"read_only": True},
            "password": {"write_only": True},
        }
