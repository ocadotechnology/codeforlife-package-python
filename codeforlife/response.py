"""
© Ocado Group
Created on 19/02/2024 at 15:31:09(+00:00).

Override default response objects.
"""

import typing as t

from rest_framework import status as _status
from rest_framework.response import Response as _Response

from .types import JsonValue


# pylint: disable-next=missing-class-docstring
class Response(_Response):
    # pylint: disable-next=useless-parent-delegation,missing-function-docstring
    def json(self) -> JsonValue:
        # pylint: disable-next=no-member
        return super().json()  # type: ignore[misc]


class NonFieldErrorsResponse(Response):
    """When errors occur that are not tied to one data field in the request."""

    def __init__(self, data: t.List[str], **kwargs):
        kwargs["data"] = {"non_field_errors": data}
        kwargs["status"] = _status.HTTP_400_BAD_REQUEST
        super().__init__(**kwargs)
