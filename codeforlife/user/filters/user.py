"""
© Ocado Group
Created on 03/04/2024 at 16:37:44(+01:00).
"""

import typing as t

from django.db.models.query import QuerySet

from ...filters import FilterSet
from ..models import User

from django_filters import (  # type: ignore[import-untyped] # isort: skip
    rest_framework as filters,
)


# pylint: disable-next=missing-class-docstring
class UserFilterSet(FilterSet):
    students_in_class = filters.CharFilter(
        "new_student__class_field__access_code",
        "exact",
    )

    teachers_in_school = filters.NumberFilter("new_teacher__school")

    _id = filters.NumberFilter(method="_id_method")
    _id_method = FilterSet.make_exclude_field_list_method("id")

    name = filters.CharFilter(method="name_method")

    def name_method(
        self: FilterSet, queryset: QuerySet[User], name: str, *args
    ):
        """Get all first names and last names that contain a substring."""
        names = t.cast(str, self.request.GET[name]).split(" ", maxsplit=1)
        first_name, last_name = (
            names if len(names) == 2 else (names[0], names[0])
        )

        # TODO: use PostgreSQL specific lookup
        # https://docs.djangoproject.com/en/5.0/ref/contrib/postgres/lookups/#std-fieldlookup-trigram_similar
        return queryset.filter(
            first_name__icontains=first_name
        ) | queryset.filter(last_name__icontains=last_name)

    class Meta:
        model = User
        fields = ["students_in_class", "teachers_in_school", "_id", "name"]
