from rest_framework.pagination import (
    LimitOffsetPagination as _LimitOffsetPagination,
)
from rest_framework.response import Response


class LimitOffsetPagination(_LimitOffsetPagination):
    default_limit = 50
    max_limit = 500

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
