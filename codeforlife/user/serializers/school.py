from rest_framework import serializers

from ..models import School


# pylint: disable-next=missing-class-docstring
class SchoolSerializer(serializers.ModelSerializer[School]):
    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "country",
            "uk_county",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
        }

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "name": instance.name,
            "country": str(instance.country),
            "uk_county": instance.county,
        }
