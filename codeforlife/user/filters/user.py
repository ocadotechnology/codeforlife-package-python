from django_filters import rest_framework as filters

from ..models import User


class UserFilterSet(filters.FilterSet):
    students_in_class = filters.CharFilter(
        "new_student__class_field__access_code", "exact"
    )

    class Meta:
        model = User
        fields = ["students_in_class"]
