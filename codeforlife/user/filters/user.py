"""
© Ocado Group
Created on 03/04/2024 at 16:37:44(+01:00).
"""

from django_filters import rest_framework as filters

from ..models import User


class UserFilterSet(filters.FilterSet):
    students_in_class = filters.CharFilter(
        "new_student__class_field",
        "exact",
    )

    class Meta:
        model = User
        fields = ["students_in_class"]
