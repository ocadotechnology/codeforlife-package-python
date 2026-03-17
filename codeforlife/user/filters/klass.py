"""
© Ocado Group
Created on 24/07/2024 at 13:19:57(+01:00).
"""

from django.db.models import Q  # isort: skip
from django.db.models.query import QuerySet  # isort: skip
from django_filters import (  # type: ignore[import-untyped] # isort: skip
    rest_framework as filters,
)

from ...filters import FilterSet  # isort: skip
from ..models import Class  # isort: skip


# pylint: disable-next=missing-class-docstring
class ClassFilterSet(FilterSet):
    _id = filters.CharFilter(method="_id__method")

    id_or_name = filters.CharFilter(method="id_or_name__method")

    def _id__method(self, queryset: QuerySet[Class], name: str, *args):
        access_codes = self.request.GET.getlist(name)
        return queryset.exclude(
            **{"_access_code_hash__sha256_in": access_codes}
        )

    def id_or_name__method(self, queryset: QuerySet[Class], _: str, value: str):
        """Get classes where the id or the name contain a substring."""
        name = value.lower()
        pks = [
            klass.pk
            for klass in queryset.only("name")
            if klass.name and name in klass.name.lower()
        ]

        return queryset.filter(
            Q(_access_code_hash__sha256=value) | Q(pk__in=pks)
        )

    class Meta:
        model = Class
        fields = ["_id", "teacher", "id_or_name"]
