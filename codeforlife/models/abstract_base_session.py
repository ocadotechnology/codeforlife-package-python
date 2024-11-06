"""
© Ocado Group
Created on 06/11/2024 at 16:44:56(+00:00).
"""

import typing as t

from django.contrib.auth import get_user_model
from django.contrib.sessions.base_session import (
    AbstractBaseSession as _AbstractBaseSession,
)
from django.db import models
from django.db.models import Manager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .abstract_base_user import AbstractBaseUser

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta

    from .base_session_store import BaseSessionStore
else:
    TypedModelMeta = object


class AbstractBaseSession(_AbstractBaseSession):
    """
    Base session class to be inherited by all session classes.
    https://docs.djangoproject.com/en/3.2/topics/http/sessions/#example
    """

    pk: str  # type: ignore[assignment]
    objects: Manager[t.Self]

    user_id: int
    user = models.OneToOneField(
        t.cast(t.Type[AbstractBaseUser], get_user_model()),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Meta(TypedModelMeta):
        abstract = True
        verbose_name = _("session")
        verbose_name_plural = _("sessions")

    @property
    def is_expired(self):
        """Whether or not this session has expired."""
        return self.expire_date < timezone.now()

    @property
    def store(self):
        """A store instance for this session."""
        return self.get_session_store_class()(self.session_key)

    @classmethod
    def get_session_store_class(cls) -> t.Type["BaseSessionStore"]:
        raise NotImplementedError
