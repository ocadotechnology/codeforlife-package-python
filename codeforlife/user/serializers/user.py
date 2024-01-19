"""
© Ocado Group
Created on 19/01/2024 at 11:06:00(+00:00).
"""

from rest_framework import serializers

from ..models import User
from .student import StudentSerializer
from .teacher import TeacherSerializer


# pylint: disable-next=missing-class-docstring
class UserSerializer(serializers.ModelSerializer[User]):
    student = StudentSerializer(
        source="new_student",
        read_only=True,
    )

    teacher = TeacherSerializer(
        source="new_teacher",
        read_only=True,
    )

    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta:
        model = User
        fields = [
            "student",
            "teacher",
            "id",
            "password",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "date_joined",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True},
            "is_active": {"read_only": True},
            "date_joined": {"read_only": True},
        }

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": instance.email,
            "is_active": instance.is_active,
            "date_joined": instance.date_joined,
            "student": StudentSerializer(instance.student).data
            if instance.student and instance.student.class_field
            else None,
            "teacher": TeacherSerializer(instance.teacher).data
            if instance.teacher
            else None,
        }
