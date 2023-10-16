from django_filters import rest_framework as filters

from ..models import User


class UserFilterSet(filters.FilterSet):
    student__klass = filters.CharFilter(
        "new_student__class_field__access_code", "exact"
    )

    class Meta:
        model = User
        fields = ["student__klass"]
