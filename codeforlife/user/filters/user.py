"""
© Ocado Group
Created on 03/04/2024 at 16:37:44(+01:00).
"""

import typing as t

from django.db.models import Q  # isort: skip
from django.db.models.query import QuerySet  # isort: skip
from django_filters import (  # type: ignore[import-untyped] # isort: skip
    rest_framework as filters,
)

from ...filters import FilterSet  # isort: skip
from ..models import (  # isort: skip
    User,
    TeacherUser,
    StudentUser,
    IndependentUser,
)


# pylint: disable-next=missing-class-docstring
class UserFilterSet(FilterSet):
    students_in_class = filters.CharFilter(
        "new_student__class_field__access_code",
        "exact",
    )

    _id = filters.NumberFilter(method="_id__method")
    _id__method = FilterSet.make_exclude_field_list_method("id")

    name = filters.CharFilter(method="name__method")

    type = filters.ChoiceFilter(
        choices=[
            ("teacher", "teacher"),
            ("student", "student"),
            ("independent", "independent"),
            ("indy", "independent"),
        ],
        method="type__method",
    )

    def name__method(
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
            Q(first_name__icontains=first_name)
            | Q(last_name__icontains=last_name)
        )

    def type__method(
        self: FilterSet,
        queryset: QuerySet[User],
        _: str,
        value: t.Literal["teacher", "student", "independent"],
    ):
        """Get users of a specific type."""
        if value == "teacher":
            return TeacherUser.objects.filter_users(queryset)
        if value == "student":
            return StudentUser.objects.filter_users(queryset)
        return IndependentUser.objects.filter_users(queryset)

    class Meta:
        model = User
        fields = ["students_in_class", "type", "_id", "name"]
