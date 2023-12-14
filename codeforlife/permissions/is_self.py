"""
© Ocado Group
Created on 12/12/2023 at 15:08:08(+00:00).
"""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsSelf(BasePermission):
    """Request's user must be the selected user."""

    def __init__(self, keyword: str = "pk"):
        """Initialize permission.

        Args:
            keyword: The key for the url kwargs that contains the user's primary
                key.
        """

        super().__init__()
        self.keyword = keyword

    def has_permission(self, request: Request, view: APIView):
        return request.user.pk == view.kwargs[self.keyword]
