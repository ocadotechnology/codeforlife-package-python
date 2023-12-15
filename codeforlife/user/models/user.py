"""
© Ocado Group
Created on 04/12/2023 at 17:19:37(+00:00).

User model.
"""

import typing as t

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_stubs_ext.db.models import TypedModelMeta

from ...models import WarehouseModel
from . import auth_factor as _auth_factor
from . import otp_bypass_token as _otp_bypass_token
from . import session as _session
from . import student as _student
from . import teacher as _teacher


class User(AbstractBaseUser, WarehouseModel, PermissionsMixin):
    """A user within the CFL system."""

    USERNAME_FIELD = "id"

    class Manager(BaseUserManager["User"], WarehouseModel.Manager["User"]):
        """
        https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#writing-a-manager-for-a-custom-user-model

        Custom user manager for custom user model.
        """

        def create(self, **kwargs):
            """Prevent calling create to maintain data integrity."""

            raise IntegrityError("Must call create_user instead.")

        def _create_user(
            self,
            password: str,
            email: t.Optional[str] = None,
            **fields,
        ):
            if email:
                email = self.normalize_email(email)

            user = User(
                **fields,
                password=make_password(password),
                email=email,
            )
            user.save(using=self._db, _from_manager=True)
            return user

        def create_user(self, password: str, first_name: str, **fields):
            """Create a user.

            https://github.com/django/django/blob/19bc11f636ca2b5b80c3d9ad5b489e43abad52bb/django/contrib/auth/models.py#L149C9-L149C20

            Args:
                password: The user's non-hashed password.
                first_name: The user's first name.

            Returns:
                A user instance.
            """

            fields.setdefault("is_staff", False)
            fields.setdefault("is_superuser", False)
            return self._create_user(password, first_name=first_name, **fields)

        def create_superuser(self, password: str, first_name: str, **fields):
            """Create a super user.

            https://github.com/django/django/blob/19bc11f636ca2b5b80c3d9ad5b489e43abad52bb/django/contrib/auth/models.py#L154C9-L154C25

            Args:
                password: The user's non-hashed password.
                first_name: The user's first name.

            Raises:
                ValueError: If is_staff is not True.
                ValueError: If is_superuser is not True.

            Returns:
                A user instance.
            """

            fields.setdefault("is_staff", True)
            fields.setdefault("is_superuser", True)

            if fields.get("is_staff") is not True:
                raise ValueError("Superuser must have is_staff=True.")
            if fields.get("is_superuser") is not True:
                raise ValueError("Superuser must have is_superuser=True.")

            return self._create_user(password, first_name=first_name, **fields)

    objects: Manager = Manager()

    session: "_session.Session"
    auth_factors: QuerySet["_auth_factor.AuthFactor"]
    otp_bypass_tokens: QuerySet["_otp_bypass_token.OtpBypassToken"]

    first_name = models.CharField(
        _("first name"),
        max_length=150,
    )

    last_name = models.CharField(
        _("last name"),
        max_length=150,
        null=True,
        blank=True,
    )

    email = models.EmailField(
        _("email address"),
        unique=True,
        null=True,
        blank=True,
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
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active."
            " Unselect this instead of deleting accounts."
        ),
    )

    date_joined = models.DateTimeField(
        _("date joined"),
        default=timezone.now,
        editable=False,
    )

    otp_secret = models.CharField(
        _("OTP secret"),
        max_length=40,
        null=True,
        editable=False,
        help_text=_("Secret used to generate a OTP."),
    )

    last_otp_for_time = models.DateTimeField(
        _("last OTP for-time"),
        null=True,
        editable=False,
        help_text=_(
            "Used to prevent replay attacks, where the same OTP is used for"
            " different times."
        ),
    )

    teacher_id: t.Optional[int]
    teacher: t.Optional[
        "_teacher.Teacher"
    ] = models.OneToOneField(  # type: ignore[assignment]
        "user.Teacher",
        null=True,
        editable=False,
        on_delete=models.CASCADE,
    )

    student_id: t.Optional[int]
    student: t.Optional[
        "_student.Student"
    ] = models.OneToOneField(  # type: ignore[assignment]
        "user.Student",
        null=True,
        editable=False,
        on_delete=models.CASCADE,
    )

    class Meta(TypedModelMeta):
        verbose_name = _("user")
        verbose_name_plural = _("users")
        constraints = [
            # pylint: disable=unsupported-binary-operation
            models.CheckConstraint(
                check=~Q(
                    teacher__isnull=False,
                    student__isnull=False,
                ),
                name="user__profile",
            ),
            models.CheckConstraint(
                check=(
                    Q(
                        teacher__isnull=False,
                        email__isnull=False,
                    )
                    | Q(
                        student__isnull=False,
                        email__isnull=True,
                    )
                    | Q(
                        teacher__isnull=True,
                        student__isnull=True,
                        email__isnull=False,
                    )
                ),
                name="user__email",
            ),
            models.CheckConstraint(
                check=(
                    Q(
                        teacher__isnull=False,
                        last_name__isnull=False,
                    )
                    | Q(
                        student__isnull=False,
                        last_name__isnull=True,
                    )
                    | Q(
                        teacher__isnull=True,
                        student__isnull=True,
                        last_name__isnull=False,
                    )
                ),
                name="user__last_name",
            ),
            models.CheckConstraint(
                check=~Q(
                    student__isnull=False,
                    is_staff=True,
                ),
                name="user__is_staff",
            ),
            models.CheckConstraint(
                check=~Q(
                    student__isnull=False,
                    is_superuser=True,
                ),
                name="user__is_superuser",
            ),
            # pylint: enable=unsupported-binary-operation
        ]

    @property
    def is_authenticated(self):
        """Check if the user has any pending auth factors."""

        try:
            return (
                self.is_active
                and not self.session.session_auth_factors.exists()
            )
        except _session.Session.DoesNotExist:
            return False

    def save(self, *args, **kwargs):
        if self.id is None and not kwargs.pop("_from_manager", False):
            raise IntegrityError("Must call create_user from manager instead.")

        if (
            self.student
            # pylint: disable-next=no-member
            and self.student.klass.students.filter(
                user__first_name=self.first_name
            ).exists()
        ):
            raise IntegrityError(
                "Another student in the class already has first name"
                f' "{self.first_name}".'
            )

        super().save(*args, **kwargs)
