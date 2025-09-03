# pylint: disable=duplicate-code
"""
© Ocado Group
Created on 12/12/2023 at 13:55:47(+00:00).
"""

import typing as t

from ...permissions import IsAuthenticated
from ..models import IndependentUser, User


class IsIndependent(IsAuthenticated):
    """Request's user must be independent."""

    def __init__(
        self,
        is_requesting_to_join_class: t.Optional[bool] = None,
    ):
        # pylint: disable=line-too-long
        """Initialize permission.

        Args:
            is_requesting_to_join_class: Check if the independent is (not)
            requesting to join a class. If None, don't check.
        """
        # pylint: enable=line-too-long
        super().__init__()

        self.is_requesting_to_join_class = is_requesting_to_join_class

    def has_permission(self, request, view):
        user = request.user
        if (
            not super().has_permission(request, view)
            or not isinstance(user, User)
            or not IndependentUser.objects.filter(id=user.id).exists()
        ):
            return False

        user = user.as_type(IndependentUser)
        return (
            self.is_requesting_to_join_class is None
            or (
                self.is_requesting_to_join_class
                and user.student.pending_class_request is not None
            )
            or (
                not self.is_requesting_to_join_class
                and user.student.pending_class_request is None
            )
        )
