# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 05/02/2024 at 09:50:04(+00:00).
"""

import typing as t
from datetime import datetime, timedelta

from django.conf import settings

# pylint: disable-next=imported-auth-user
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as _UserManager
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pyotp import TOTP

from ....models import AbstractBaseUser, DataEncryptionKeyModel
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


AnyUser = t.TypeVar("AnyUser", bound="User")


class UserManager(
    _UserManager[AnyUser],
    DataEncryptionKeyModel.Manager[AnyUser],
    t.Generic[AnyUser],
):
    """
    Manager for the User model that inherits Django's default manager and
    encrypted manager to handle encrypted fields.
    """

    def filter_users(self, queryset: QuerySet["User"]):
        """Filter the users to the specific type.

        Args:
            queryset: The queryset of users to filter.

        Returns:
            A subset of the queryset of users.
        """
        return queryset

    # pylint: disable-next=missing-function-docstring
    def get_queryset(self):
        queryset = super().get_queryset()
        return (
            queryset
            if getattr(settings, "OLD_SYSTEM", True)
            else self.filter_users(queryset.filter(is_active=True))
        )


# pylint: disable-next=too-many-ancestors
class User(
    _AbstractBaseUser,
    AbstractUser,  # TODO: remove this inheritance in new schema
    DataEncryptionKeyModel,
):
    """A proxy to Django's user class."""

    associated_data = "user"

    _password: t.Optional[str]

    id: int  # type: ignore[assignment]
    auth_factors: QuerySet["AuthFactor"]  # type: ignore[assignment,misc]
    # pylint: disable-next=line-too-long
    otp_bypass_tokens: QuerySet["OtpBypassToken"]  # type: ignore[assignment,misc]
    session: "Session"  # type: ignore[assignment]
    userprofile: "UserProfile"

    credential_fields = frozenset(["email", "password"])

    # TODO: remove in new schema
    password: str  # type: ignore[assignment]
    password = models.CharField(  # type: ignore[assignment]
        _("password"),
        max_length=128,
    )

    # TODO: remove in new schema
    last_login: t.Optional[datetime]  # type: ignore[assignment]
    last_login = models.DateTimeField(  # type: ignore[assignment]
        _("last login"),
        blank=True,
        null=True,
    )

    objects: UserManager[  # type: ignore[misc]
        "User"
    ] = UserManager()  # type: ignore[assignment]

    @property
    def is_authenticated(self):
        return (
            True
            if getattr(settings, "OLD_SYSTEM", True)
            else (
                not self.session.auth_factors.exists()
                and self.userprofile.is_verified
                if super().is_authenticated
                else False
            )
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

    # This property is set up differently in the old and new systems, so is not
    # defined on the model in the old system.
    is_verified: bool
    # @property
    # def is_verified(self):
    #     """Shorthand for user-profile field."""
    #     return self.userprofile.is_verified

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


if not getattr(settings, "OLD_SYSTEM", True):

    def is_verified(self: User):
        """Shorthand for user-profile field."""
        return self.userprofile.is_verified

    User.is_verified = property(fget=is_verified)  # type: ignore[assignment]


class UserProfile(models.Model):
    """A user's profile."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    otp_secret = models.CharField(max_length=40, null=True, blank=True)
    last_otp_for_time = models.DateTimeField(null=True, blank=True)
    developer = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    # Google.
    google_refresh_token: t.Optional[str]
    # google_refresh_token = EncryptedCharField(
    #     # pylint: disable-next=protected-access
    #     max_length=1000 + len(EncryptedCharField._prefix),
    #     null=True,
    #     blank=True,
    # )
    google_sub: t.Optional[str]
    # google_sub = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def joined_recently(self):
        """Whether the user joined within the last week."""
        now = timezone.now()
        return now - timedelta(days=7) <= self.user.date_joined
