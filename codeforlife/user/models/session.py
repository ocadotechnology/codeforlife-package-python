# from django.db import models
# from django.utils import timezone

# from .classroom import Class
# from .school import School
# from .user import User


# class UserSession(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     login_time = models.DateTimeField(default=timezone.now)
#     school = models.ForeignKey(School, null=True, on_delete=models.SET_NULL)
#     class_field = models.ForeignKey(Class, null=True, on_delete=models.SET_NULL)
#     login_type = models.CharField(
#         max_length=100, null=True
#     )  # for student login

#     def __str__(self):
#         return f"{self.user} login: {self.login_time} type: {self.login_type}"

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
    def store(self):
        return self.get_session_store_class()(self.session_key)

    @classmethod
    def get_session_store_class(cls):
        return SessionStore


class SessionStore(DBStore):
    """
    A custom session store interface to support:
    1. creating only one session per user;
    2. clearing expired sessions per user.
    https://docs.djangoproject.com/en/3.2/topics/http/sessions/#example
    """

    @classmethod
    def get_model_class(cls):
        return Session

    def create_model_instance(self, data):
        Session = self.get_model_class()
        session: Session = None

        # Get user ID if not an anon user.
        try:
            user_id = int(data.get(SESSION_KEY))
        except (ValueError, TypeError):
            user_id = None

        if user_id:
            # Clear expired sessions for user.
            self.clear_expired(user_id)

            try:
                # Return user's non-expired session and update its data.
                session: Session = Session.objects.get(user_id=user_id)
                session.session_data = self.encode(data)
                return session
            except Session.DoesNotExist:
                # Get and set user's enabled auth factors in the session.
                user = User.objects.get(id=user_id)
        else:
            user = None

        # Create session.
        session = super().create_model_instance(data)
        session.user = user
        session.save()

        # Create session auth factors.
        if user:
            session_auth_factor.SessionAuthFactor.objects.bulk_create(
                [
                    session_auth_factor.SessionAuthFactor(
                        session=session,
                        auth_factor=auth_factor,
                    )
                    for auth_factor in user.auth_factors
                ]
            )

        return session

    @classmethod
    def clear_expired(cls, user_id: t.Optional[int] = None):
        session_query = cls.get_model_class().objects.filter(
            expire_date__lt=timezone.now()
        )
        if user_id:
            session_query = session_query.filter(user_id=user_id)
        session_query.delete()
