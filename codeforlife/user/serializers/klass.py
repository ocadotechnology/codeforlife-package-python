from rest_framework import serializers

from ..models import Class


# pylint: disable-next=missing-class-docstring
class ClassSerializer(serializers.ModelSerializer[Class]):
    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta:
        model = Class
        fields = [
            "id",
            "teacher",
            "school",
            "name",
            "read_classmates_data",
            "receive_requests_until",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def to_representation(self, instance):
        return {
            "id": instance.access_code,
            "name": instance.name,
            "read_classmates_data": instance.classmates_data_viewable,
            "receive_requests_until": instance.accept_requests_until,
            "teacher": instance.teacher.pk,
            "school": instance.teacher.school.pk,
        }
