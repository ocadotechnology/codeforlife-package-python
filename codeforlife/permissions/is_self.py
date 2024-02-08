"""
© Ocado Group
Created on 08/02/2024 at 11:19:37(+00:00).
"""

import typing as t

from rest_framework.permissions import IsAuthenticated


class IsSelf(IsAuthenticated):
    """Request's user must be the selected user."""

    def __init__(
        self,
        lookup_field: str = "pk",
        lookup_url_kwarg: t.Optional[str] = None,
    ):
        """Initialize permission.

        Args:
            lookup_field: The field used to uniquely identify a user.
            lookup_url_kwarg: The key for the url arg used to lookup the user.
        """

        super().__init__()
        self.lookup_field = lookup_field
        self.lookup_url_kwarg = lookup_url_kwarg or lookup_field

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.lookup_field == other.lookup_field
            and self.lookup_url_kwarg == other.lookup_url_kwarg
        )

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and getattr(request.user, self.lookup_field)
            == view.kwargs[self.lookup_url_kwarg]
        )
