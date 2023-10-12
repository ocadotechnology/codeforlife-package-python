import typing as t

from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest as _WSGIRequest
from django.http import HttpRequest as _HttpRequest
from rest_framework.request import Request as _Request

from .user.models import User
from .user.models.session import SessionStore


class WSGIRequest(_WSGIRequest):
    session: SessionStore
    user: t.Union[User, AnonymousUser]


class HttpRequest(_HttpRequest):
    session: SessionStore
    user: t.Union[User, AnonymousUser]


class Request(_Request):
    session: SessionStore
    user: t.Union[User, AnonymousUser]
