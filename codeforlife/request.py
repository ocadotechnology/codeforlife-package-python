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

from .types import JsonDict, JsonList
from .user.models import (
    AdminSchoolTeacherUser,
    AnyUser,
    IndependentUser,
    NonAdminSchoolTeacherUser,
    NonSchoolTeacherUser,
    SchoolTeacherUser,
    StudentUser,
    TeacherUser,
    User,
)
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
class Request(_Request, t.Generic[AnyUser]):
    session: SessionStore
    data: t.Any

    def __init__(self, user_class: t.Type[AnyUser], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_class = user_class

    @property
    def user(self):
        return t.cast(t.Union[AnyUser, AnonymousUser], super().user)

    @user.setter
    def user(self, value):
        if isinstance(value, User) and not isinstance(value, self.user_class):
            value = value.as_type(self.user_class)

        self._user = value
        self._request.user = value

    @property
    def anon_user(self):
        """The anonymous user that made the request."""
        return t.cast(AnonymousUser, self.user)

    @property
    def auth_user(self):
        """The authenticated user that made the request."""
        return t.cast(AnyUser, self.user)

    @property
    def teacher_user(self):
        """The authenticated teacher-user that made the request."""
        return self.auth_user.as_type(TeacherUser)

    @property
    def school_teacher_user(self):
        """The authenticated school-teacher-user that made the request."""
        return self.auth_user.as_type(SchoolTeacherUser)

    @property
    def admin_school_teacher_user(self):
        """The authenticated admin-school-teacher-user that made the request."""
        return self.auth_user.as_type(AdminSchoolTeacherUser)

    @property
    def non_admin_school_teacher_user(self):
        """
        The authenticated non-admin-school-teacher-user that made the request.
        """
        return self.auth_user.as_type(NonAdminSchoolTeacherUser)

    @property
    def non_school_teacher_user(self):
        """The authenticated non-school-teacher-user that made the request."""
        return self.auth_user.as_type(NonSchoolTeacherUser)

    @property
    def student_user(self):
        """The authenticated student-user that made the request."""
        return self.auth_user.as_type(StudentUser)

    @property
    def indy_user(self):
        """The authenticated independent-user that made the request."""
        return self.auth_user.as_type(IndependentUser)

    @property
    def json_dict(self):
        """The data as a json dictionary."""
        return t.cast(JsonDict, self.data)

    @property
    def json_list(self):
        """The data as a json list."""
        return t.cast(JsonList, self.data)
