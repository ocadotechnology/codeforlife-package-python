"""
© Ocado Group
Created on 15/02/2024 at 15:57:53(+00:00).
"""

from rest_framework.permissions import BasePermission as _BasePermission


class BasePermission(_BasePermission):
    """Base permission which all other permissions must inherit from."""

    def __eq__(self, other):
        return isinstance(other, self.__class__)
