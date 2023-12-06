"""
© Ocado Group
Created on 04/12/2023 at 17:20:33(+00:00).

Session model and store.
"""

import typing as t

from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.contrib.sessions.base_session import AbstractBaseSession
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from . import session_auth_factor, user


class Session(AbstractBaseSession):
    """
    A custom session model to support querying a user's session.
    https://docs.djangoproject.com/en/3.2/topics/http/sessions/#example
    """

    session_auth_factors: QuerySet["session_auth_factor.SessionAuthFactor"]

    user: "user.User" = models.OneToOneField(
        "user.User",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    @property
    def is_expired(self):
        return self.expire_date < timezone.now()

    @property
    def store(self):
        return self.get_session_store_class()(self.session_key)

    @classmethod
    def get_session_store_class(cls):
        return SessionStore


class SessionStore(DBStore):
    """
    A custom session store interface to support:
    1. creating only one session per user;
    2. setting a session's auth factors;
    3. clearing a user's expired sessions.

    https://docs.djangoproject.com/en/3.2/topics/http/sessions/#example
    """

    @classmethod
    def get_model_class(cls):
        return Session

    def create_model_instance(self, data):
        Session = self.get_model_class()
        session: Session

        try:
            user_id = int(data.get(SESSION_KEY))

            try:
                session = Session.objects.get(user_id=user_id)
            except Session.DoesNotExist:
                # Associate session to user.
                session = Session.objects.get(session_key=self.session_key)
                session.user = user.User.objects.get(id=user_id)
                session_auth_factor.SessionAuthFactor.objects.bulk_create(
                    [
                        session_auth_factor.SessionAuthFactor(
                            session=session,
                            auth_factor=auth_factor,
                        )
                        for auth_factor in session.user.auth_factors.all()
                    ]
                )

            session.session_data = self.encode(data)

        except (ValueError, TypeError):
            # Create an anon session.
            session = super().create_model_instance(data)

        return session

    @classmethod
    def clear_expired(cls, user_id: t.Optional[int] = None):
        session_query = cls.get_model_class().objects.filter(
            expire_date__lt=timezone.now()
        )
        if user_id:
            session_query = session_query.filter(user_id=user_id)
        session_query.delete()
