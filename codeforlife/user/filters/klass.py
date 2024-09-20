"""
© Ocado Group
Created on 24/07/2024 at 13:19:57(+01:00).
"""

from django_filters import (  # type: ignore[import-untyped] # isort: skip
    rest_framework as filters,
)

from ...filters import FilterSet  # isort: skip
from ..models import Class  # isort: skip


# pylint: disable-next=missing-class-docstring
class ClassFilterSet(FilterSet):
    _id = filters.CharFilter(method="_id__method")
    _id__method = FilterSet.make_exclude_field_list_method("access_code")

    class Meta:
        model = Class
        fields = ["_id", "teacher"]
