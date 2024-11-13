"""
© Ocado Group
Created on 05/11/2024 at 14:41:58(+00:00).

Custom WSGIRequest which hints to our custom types.
"""

import typing as t

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.core.handlers.wsgi import WSGIRequest as _WSGIRequest

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:
    from ..user.models import User
    from ..user.models.session import SessionStore

    AnyUser = t.TypeVar("AnyUser", bound=User)
else:
    AnyUser = t.TypeVar("AnyUser")

AnyDBStore = t.TypeVar("AnyDBStore", bound=DBStore)
AnyAbstractBaseUser = t.TypeVar("AnyAbstractBaseUser", bound=AbstractBaseUser)
# pylint: enable=duplicate-code


# pylint: disable-next=missing-class-docstring
class BaseWSGIRequest(_WSGIRequest, t.Generic[AnyDBStore, AnyAbstractBaseUser]):
    session: AnyDBStore
    user: t.Union[AnyAbstractBaseUser, AnonymousUser]


# pylint: disable-next=missing-class-docstring
class WSGIRequest(BaseWSGIRequest["SessionStore", AnyUser], t.Generic[AnyUser]):
    pass
