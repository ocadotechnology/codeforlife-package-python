"""
© Ocado Group
Created on 11/04/2024 at 11:22:25(+01:00).
"""

from django.conf import settings
from rest_framework.pagination import (
    LimitOffsetPagination as _LimitOffsetPagination,
)
from rest_framework.response import Response


class LimitOffsetPagination(_LimitOffsetPagination):
    """Default pagination class for all list actions."""

    # Set larger limits when debugging to avoid having to paginate lists.
    # When deployed, the limits should be reasonable for performance reasons.
    default_limit = 1000000 if settings.DEBUG else 50
    max_limit = 1000000 if settings.DEBUG else 150

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.count,
                "offset": self.offset,
                "limit": self.limit,
                "max_limit": self.max_limit,
                "data": data,
            }
        )
