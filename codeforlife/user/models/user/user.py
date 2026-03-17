# TODO: remove this in new system
# mypy: disable-error-code="import-untyped"
"""
© Ocado Group
Created on 05/02/2024 at 09:50:04(+00:00).
"""

import typing as t
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import UserManager as _UserManager
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pyotp import TOTP

from ....models import AbstractBaseUser, DataEncryptionKeyModel
from ....models.fields import EncryptedTextField, Sha256Field
from ....types import Validators
from ....validators import UnicodeAlphanumericCharSetValidator

if t.TYPE_CHECKING:  # pragma: no cover
    from ..auth_factor import AuthFactor
    from ..otp_bypass_token import OtpBypassToken
    from ..session import Session
    from ..student import Student
    from ..teacher import Teacher


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

    def _create_user_object(
        self,
        _: t.Literal[""],  # username is not used but is required by the parent
        email: t.Optional[str],
        password: t.Optional[str],
        **extra_fields,
    ):
        user = self.model(**extra_fields)
        user.email = email
        user.password = make_password(password)
        user.first_name = extra_fields.get("first_name", "")
        user.last_name = extra_fields.get("last_name", "")
        return user

    # pylint: disable=missing-function-docstring

    @classmethod
    def normalize_email(cls, email):
        return None if email is None else email.lower()

    def create_user(  # type: ignore[override]
        self,
        email: t.Optional[str] = None,
        password: t.Optional[str] = None,
        **extra_fields,
    ):
        return super().create_user(
            username="", email=email, password=password, **extra_fields
        )

    def acreate_user(  # type: ignore[override]
        self,
        email: t.Optional[str] = None,
        password: t.Optional[str] = None,
        **extra_fields,
    ):
        return super().acreate_user(
            username="", email=email, password=password, **extra_fields
        )

    def create_superuser(  # type: ignore[override]
        self,
        email: t.Optional[str] = None,
        password: t.Optional[str] = None,
        **extra_fields,
    ):
        return super().create_superuser(
            username="", email=email, password=password, **extra_fields
        )

    def acreate_superuser(  # type: ignore[override]
        self,
        email: t.Optional[str] = None,
        password: t.Optional[str] = None,
        **extra_fields,
    ):
        return super().acreate_superuser(
            username="", email=email, password=password, **extra_fields
        )

    # pylint: enable=missing-function-docstring

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


# pylint: disable-next=too-many-ancestors,too-many-instance-attributes
class User(AbstractBaseUser, PermissionsMixin, DataEncryptionKeyModel):
    """A Code for Life user."""

    ### Type hints for fields and related objects.
    _password: t.Optional[str]
    id: int  # type: ignore[assignment]
    auth_factors: QuerySet["AuthFactor"]  # type: ignore[assignment,misc]
    # pylint: disable-next=line-too-long
    otp_bypass_tokens: QuerySet["OtpBypassToken"]  # type: ignore[assignment,misc]
    session: "Session"  # type: ignore[assignment]
    userprofile: "UserProfile"

    ### Data encryption key model configuration.
    associated_data = "user"

    ### Django auth field registries.
    EMAIL_FIELD = "_email"
    USERNAME_FIELD = "_email_hash"
    REQUIRED_FIELDS = ["_email"]

    ### Custom field registries.
    CREDENTIAL_FIELDS = frozenset(["email", "password"])
    FIRST_NAME_FIELDS = frozenset(["_first_name", "_first_name_hash"])
    EMAIL_FIELDS = frozenset(["_email", "_email_hash"])

    ### First name fields.
    _first_name_hash = Sha256Field(
        verbose_name=_("first name hash"),
        db_column="first_name_hash",
        null=True,
    )
    _first_name = EncryptedTextField(
        associated_data="first_name",
        null=True,
        verbose_name=_("first name"),
        db_column="first_name",
    )

    @property
    def first_name(self):
        """The user's first name."""
        return self._first_name

    @first_name.setter
    def first_name(self, value: str):
        """Set first name and hash immediately."""
        self._first_name = value
        self._first_name_hash = value

    ### Email fields.
    _email_hash = Sha256Field(
        verbose_name=_("email hash"),
        unique=True,
        null=True,
        db_column="email_hash",
    )
    _email = EncryptedTextField(
        associated_data="email",
        null=True,
        verbose_name=_("email address"),
        db_column="email",
    )

    @property
    def email(self):
        """The user's email address."""
        return self._email

    @email.setter
    def email(self, value: t.Optional[str]):
        """Set the user's email address."""
        value = self.__class__.objects.normalize_email(value)
        self._email = value
        self._email_hash = value

    ### Other fields.
    last_name = EncryptedTextField(
        associated_data="last_name", null=True, verbose_name=_("last name")
    )

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
        ),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

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
            _first_name=self._first_name,
            _first_name_hash=self._first_name_hash,
            last_name=self.last_name,
            is_active=self.is_active,
            _email=self._email,
            _email_hash=self._email_hash,
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
                # pylint: disable=duplicate-code
                *self.FIRST_NAME_FIELDS,
                *self.EMAIL_FIELDS,
                "last_name",
                "is_active",
                # pylint: enable=duplicate-code
            ]
        )

        # self.userprofile.google_refresh_token = None
        # self.userprofile.google_sub = None
        # self.userprofile.save(
        #     update_fields=[
        #         "google_refresh_token",
        #         "google_sub",
        #     ]
        # )

    def __repr__(self):
        return f"<User: {self.email}>"


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
