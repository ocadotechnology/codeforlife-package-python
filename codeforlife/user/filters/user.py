"""
© Ocado Group
Created on 03/04/2024 at 16:37:44(+01:00).
"""

from django_filters import (  # type: ignore[import-untyped] # isort: skip
    rest_framework as filters,
)

from ...filters import FilterSet
from ..models import User


# pylint: disable-next=missing-class-docstring
class UserFilterSet(FilterSet):
    students_in_class = filters.CharFilter(
        "new_student__class_field__access_code",
        "exact",
    )

    teachers_in_school = filters.NumberFilter("new_teacher__school")

    _id = filters.NumberFilter(method="_id_method")
    _id_method = FilterSet.make_exclude_field_list_method("id")

    class Meta:
        model = User
        fields = ["students_in_class", "teachers_in_school", "_id"]
