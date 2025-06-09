"""
© Ocado Group
Created on 20/02/2024 at 15:31:38(+00:00).
"""

import typing as t

from django.db.models.query import QuerySet

from ...models import AbstractBaseSession, BaseSessionStore
from .user import User

if t.TYPE_CHECKING:  # pragma: no cover
    from .session_auth_factor import SessionAuthFactor


class Session(AbstractBaseSession):
    """
    A custom session model to support querying a user's session.
    https://docs.djangoproject.com/en/5.1/topics/http/sessions/#example
    """

    auth_factors: QuerySet["SessionAuthFactor"]

    user = AbstractBaseSession.init_user_field(User)

    @classmethod
    def get_session_store_class(cls):
        return SessionStore


class SessionStore(BaseSessionStore[Session, User]):
    """
    A custom session store interface to support:
    1. creating only one session per user;
    2. setting a session's auth factors;
    3. clearing a user's expired sessions.
    https://docs.djangoproject.com/en/5.1/topics/http/sessions/#example
    """

    def associate_session_to_user(self, session, user_id):
        # pylint: disable-next=import-outside-toplevel
        from .session_auth_factor import SessionAuthFactor

        super().associate_session_to_user(session, user_id)
        SessionAuthFactor.objects.bulk_create(
            [
                SessionAuthFactor(session=session, auth_factor=auth_factor)
                for auth_factor in session.user.auth_factors.all()
            ]
        )
