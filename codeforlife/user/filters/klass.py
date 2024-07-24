"""
© Ocado Group
Created on 24/07/2024 at 13:19:57(+01:00).
"""

from django_filters import (  # type: ignore[import-untyped] # isort: skip
    rest_framework as filters,
)

from ..models import Class


# pylint: disable-next=missing-class-docstring
class ClassFilterSet(filters.FilterSet):
    class Meta:
        model = Class
        fields = ["teacher"]
