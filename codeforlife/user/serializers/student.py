from rest_framework import serializers

from ..models import Student


class StudentSerializer(serializers.ModelSerializer[Student]):
    class Meta:
        model = Student
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
        }
