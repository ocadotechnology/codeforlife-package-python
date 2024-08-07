"""
© Ocado Group
Created on 24/07/2024 at 13:19:57(+01:00).
"""

from ...filters import FilterSet
from ..models import Class


# pylint: disable-next=missing-class-docstring
class ClassFilterSet(FilterSet):
    class Meta:
        model = Class
        fields = ["teacher"]
