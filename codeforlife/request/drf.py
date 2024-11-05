"""
© Ocado Group
Created on 05/11/2024 at 14:41:58(+00:00).

Custom Request which hints to our custom types.
"""

import typing as t

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.contrib.sessions.backends.db import SessionStore as DBStore
from rest_framework.request import Request as _Request

from ..types import JsonDict, JsonList

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


# pylint: disable-next=missing-class-docstring,abstract-method
class BaseRequest(_Request, t.Generic[AnyDBStore, AnyAbstractBaseUser]):
    data: t.Any
    session: AnyDBStore
    user: t.Union[AnyAbstractBaseUser, AnonymousUser]

    @property
    def query_params(self) -> t.Dict[str, str]:  # type: ignore[override]
        return super().query_params

    @property
    def anon_user(self):
        """The anonymous user that made the request."""
        return t.cast(AnonymousUser, self.user)

    @property
    def auth_user(self):
        """The authenticated user that made the request."""
        return t.cast(AnyAbstractBaseUser, self.user)

    @property
    def json_dict(self):
        """The data as a json dictionary."""
        return t.cast(JsonDict, self.data)

    @property
    def json_list(self):
        """The data as a json list."""
        return t.cast(JsonList, self.data)


# pylint: disable-next=missing-class-docstring,abstract-method
class Request(BaseRequest["SessionStore", AnyUser], t.Generic[AnyUser]):
    def __init__(self, user_class: t.Type[AnyUser], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_class = user_class

    @property
    def user(self):
        return t.cast(t.Union[AnyUser, AnonymousUser], super().user)

    @user.setter
    def user(self, value):
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import User

        if (
            isinstance(value, User)
            and issubclass(self.user_class, User)
            and not isinstance(value, self.user_class)
        ):
            value = value.as_type(self.user_class)

        self._user = value
        self._request.user = value

    @property
    def teacher_user(self):
        """The authenticated teacher-user that made the request."""
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import TeacherUser

        return self.auth_user.as_type(TeacherUser)

    @property
    def school_teacher_user(self):
        """The authenticated school-teacher-user that made the request."""
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import SchoolTeacherUser

        return self.auth_user.as_type(SchoolTeacherUser)

    @property
    def admin_school_teacher_user(self):
        """The authenticated admin-school-teacher-user that made the request."""
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import AdminSchoolTeacherUser

        return self.auth_user.as_type(AdminSchoolTeacherUser)

    @property
    def non_admin_school_teacher_user(self):
        """
        The authenticated non-admin-school-teacher-user that made the request.
        """
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import NonAdminSchoolTeacherUser

        return self.auth_user.as_type(NonAdminSchoolTeacherUser)

    @property
    def non_school_teacher_user(self):
        """The authenticated non-school-teacher-user that made the request."""
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import NonSchoolTeacherUser

        return self.auth_user.as_type(NonSchoolTeacherUser)

    @property
    def student_user(self):
        """The authenticated student-user that made the request."""
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import StudentUser

        return self.auth_user.as_type(StudentUser)

    @property
    def indy_user(self):
        """The authenticated independent-user that made the request."""
        # pylint: disable-next=import-outside-toplevel
        from ..user.models import IndependentUser

        return self.auth_user.as_type(IndependentUser)
