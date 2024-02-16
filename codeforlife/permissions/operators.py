"""
© Ocado Group
Created on 02/02/2024 at 17:52:37(+00:00).

Extends the permission operands provided by Django REST framework.
"""

import typing as t

from rest_framework.permissions import AND as _AND
from rest_framework.permissions import NOT as _NOT
from rest_framework.permissions import OR as _OR

from .base import BasePermission


# pylint: disable-next=missing-class-docstring
class AND(_AND):
    op1: BasePermission
    op2: BasePermission

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.op1 == other.op1
            and self.op2 == other.op2
        )


# pylint: disable-next=missing-class-docstring
class NOT(_NOT):
    op1: BasePermission

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.op1 == other.op1


# pylint: disable-next=missing-class-docstring
class OR(_OR):
    op1: BasePermission
    op2: BasePermission

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.op1 == other.op1
            and self.op2 == other.op2
        )


Permission = t.Union[BasePermission, AND, NOT, OR]
