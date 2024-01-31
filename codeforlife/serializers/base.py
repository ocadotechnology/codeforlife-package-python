"""
© Ocado Group
Created on 29/01/2024 at 14:27:09(+00:00).

Base serializer.
"""

import typing as t

from django.contrib.auth.models import AnonymousUser
from rest_framework.serializers import BaseSerializer as _BaseSerializer

from ..request import Request
from ..user.models import User


# pylint: disable-next=abstract-method
class BaseSerializer(_BaseSerializer):
    """Base serializer to be inherited by all other serializers."""

    @property
    def request(self):
        """The HTTP request that triggered the view."""

        return t.cast(Request, self.context["request"])

    @property
    def request_user(self):
        """
        The user that made the request. Assumes the user has authenticated.
        """

        return t.cast(User, self.request.user)

    @property
    def request_anon_user(self):
        """
        The user that made the request. Assumes the user has not authenticated.
        """

        return t.cast(AnonymousUser, self.request.user)
