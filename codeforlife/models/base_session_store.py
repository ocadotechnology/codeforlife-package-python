"""
© Ocado Group
Created on 06/11/2024 at 17:31:32(+00:00).
"""

import typing as t

from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone

from ..types import get_arg

if t.TYPE_CHECKING:
    from .abstract_base_session import AbstractBaseSession
    from .abstract_base_user import AbstractBaseUser

    AnyAbstractBaseSession = t.TypeVar(
        "AnyAbstractBaseSession", bound=AbstractBaseSession
    )
    AnyAbstractBaseUser = t.TypeVar(
        "AnyAbstractBaseUser", bound=AbstractBaseUser
    )
else:
    AnyAbstractBaseSession = t.TypeVar("AnyAbstractBaseSession")
    AnyAbstractBaseUser = t.TypeVar("AnyAbstractBaseUser")


class BaseSessionStore(
    SessionStore,
    t.Generic[AnyAbstractBaseSession, AnyAbstractBaseUser],
):
    """
    Base session store class to be inherited by all session store classes.
    https://docs.djangoproject.com/en/5.1/topics/http/sessions/#example
    """

    @classmethod
    def get_model_class(cls) -> t.Type[AnyAbstractBaseSession]:
        return get_arg(cls, 0)

    @classmethod
    def get_user_class(cls) -> t.Type[AnyAbstractBaseUser]:
        """Get the user class."""
        return get_arg(cls, 1)

    def associate_session_to_user(
        self, session: AnyAbstractBaseSession, user_id: int
    ):
        """Associate an anon session to a user.

        Args:
            session: The anon session.
            user_id: The user to associate.
        """
        objects = self.get_user_class().objects  # type: ignore[attr-defined]
        session.user = objects.get(id=user_id)  # type: ignore[attr-defined]

    def create_model_instance(self, data):
        try:
            user_id = int(data.get(SESSION_KEY))
        except (ValueError, TypeError):
            # Create an anon session.
            return super().create_model_instance(data)

        model_class = self.get_model_class()

        try:
            session = model_class.objects.get(
                user_id=user_id,  # type: ignore[misc]
            )
        except model_class.DoesNotExist:
            session = model_class.objects.get(session_key=self.session_key)
            self.associate_session_to_user(
                t.cast(AnyAbstractBaseSession, session), user_id
            )

        session.session_data = self.encode(data)

        return session

    @classmethod
    def clear_expired(cls, user_id=None):
        session_query = cls.get_model_class().objects.filter(
            expire_date__lt=timezone.now()
        )

        if user_id is not None:
            session_query = session_query.filter(user_id=user_id)

        session_query.delete()
