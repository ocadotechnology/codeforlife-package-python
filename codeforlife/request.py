"""
© Ocado Group
Created on 19/02/2024 at 15:28:22(+00:00).

Override default request objects.
"""

import typing as t

from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest as _WSGIRequest
from django.http import HttpRequest as _HttpRequest
from rest_framework.request import Request as _Request

from .user.models import User
from .user.models.session import SessionStore


# pylint: disable-next=missing-class-docstring
class WSGIRequest(_WSGIRequest):
    session: SessionStore
    user: t.Union[User, AnonymousUser]


# pylint: disable-next=missing-class-docstring
class HttpRequest(_HttpRequest):
    session: SessionStore
    user: t.Union[User, AnonymousUser]


# pylint: disable-next=missing-class-docstring,abstract-method
class Request(_Request):
    session: SessionStore
    user: t.Union[User, AnonymousUser]
