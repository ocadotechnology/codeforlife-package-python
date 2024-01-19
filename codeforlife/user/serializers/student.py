from rest_framework import serializers

from ..models import Student


# pylint: disable-next=missing-class-docstring
class StudentSerializer(serializers.ModelSerializer[Student]):
    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta:
        model = Student
        fields = [
            "id",
            "klass",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "klass": instance.class_field.access_code,
            "school": instance.class_field.teacher.school.pk,
        }
