# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 05/02/2024 at 09:50:04(+00:00).
"""

import typing as t
from datetime import datetime

from common.models import UserProfile

# pylint: disable-next=imported-auth-user
from django.contrib.auth.models import User as _User
from django.contrib.auth.models import UserManager as _UserManager
from django.db.models.query import QuerySet
from pyotp import TOTP

from ....models import AbstractBaseUser
from ....types import Validators
from ....validators import UnicodeAlphanumericCharSetValidator

if t.TYPE_CHECKING:  # pragma: no cover
    from django_stubs_ext.db.models import TypedModelMeta

    from ..auth_factor import AuthFactor
    from ..otp_bypass_token import OtpBypassToken
    from ..session import Session
    from ..student import Student
    from ..teacher import Teacher
else:
    TypedModelMeta = object


# TODO: add to model validators in new schema.
user_first_name_validators: Validators = [
    UnicodeAlphanumericCharSetValidator(
        spaces=True,
        special_chars="-'",
    )
]
user_last_name_validators: Validators = [
    UnicodeAlphanumericCharSetValidator(
        spaces=True,
        special_chars="-'",
    )
]


# TODO: remove in new schema
class _AbstractBaseUser(AbstractBaseUser):
    password: str = None  # type: ignore[assignment]
    last_login: datetime = None  # type: ignore[assignment]

    class Meta(TypedModelMeta):
        abstract = True


# pylint: disable-next=too-many-ancestors
class User(_AbstractBaseUser, _User):
    """A proxy to Django's user class."""

    _password: t.Optional[str]

    id: int  # type: ignore[assignment]
    auth_factors: QuerySet["AuthFactor"]  # type: ignore[assignment]
    otp_bypass_tokens: QuerySet["OtpBypassToken"]  # type: ignore[assignment]
    session: "Session"  # type: ignore[assignment]
    userprofile: UserProfile

    credential_fields = frozenset(["email", "password"])

    class Meta(TypedModelMeta):
        proxy = True

    @property
    def is_authenticated(self):
        return (
            not self.session.auth_factors.exists()
            and self.userprofile.is_verified
            if super().is_authenticated
            else False
        )

    @property
    def student(self) -> t.Optional["Student"]:
        """A user's student-profile."""
        # pylint: disable-next=import-outside-toplevel
        from ..student import Student

        try:
            # pylint: disable-next=no-member
            return self.new_student  # type: ignore[attr-defined]
        except Student.DoesNotExist:
            return None

    @property
    def teacher(self) -> t.Optional["Teacher"]:
        """A user's teacher-profile."""
        # pylint: disable-next=import-outside-toplevel
        from ..teacher import Teacher

        try:
            # pylint: disable-next=no-member
            return self.new_teacher  # type: ignore[attr-defined]
        except Teacher.DoesNotExist:
            return None

    @property
    def otp_secret(self):
        """Shorthand for user-profile field."""
        return self.userprofile.otp_secret

    @property
    def last_otp_for_time(self):
        """Shorthand for user-profile field."""
        return self.userprofile.last_otp_for_time

    @property
    def is_verified(self):
        """Shorthand for user-profile field."""
        return self.userprofile.is_verified

    @property
    def totp(self):
        """Time-based one-time-password for user."""
        return TOTP(self.otp_secret)

    @property
    def totp_provisioning_uri(self):
        """URI provision for the user's time-based one-time-password."""
        return self.totp.provisioning_uri(
            name=self.email,
            issuer_name="Code for Life",
        )

    def as_type(self, user_class: t.Type["AnyUser"]):
        """Convert this generic user to a typed user.

        Args:
            user_class: The type of user to convert to.

        Returns:
            An instance of the typed user.
        """
        return user_class(
            pk=self.pk,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            is_active=self.is_active,
            email=self.email,
            is_staff=self.is_staff,
            date_joined=self.date_joined,
            is_superuser=self.is_superuser,
            password=self.password,
            last_login=self.last_login,
        )

    def anonymize(self):
        """Anonymize the user."""
        self.first_name = ""
        self.last_name = ""
        self.email = ""
        self.is_active = False
        self.save(
            update_fields=[
                "first_name",
                "last_name",
                "email",
                "username",
                "is_active",
            ]
        )

        self.userprofile.google_refresh_token = None
        self.userprofile.google_sub = None
        self.userprofile.save(
            update_fields=[
                "google_refresh_token",
                "google_sub",
            ]
        )


AnyUser = t.TypeVar("AnyUser", bound=User)


# pylint: disable-next=missing-class-docstring
class UserManager(_UserManager[AnyUser], t.Generic[AnyUser]):
    def filter_users(self, queryset: QuerySet[User]):
        """Filter the users to the specific type.

        Args:
            queryset: The queryset of users to filter.

        Returns:
            A subset of the queryset of users.
        """
        return queryset

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        return self.filter_users(super().get_queryset().filter(is_active=True))
