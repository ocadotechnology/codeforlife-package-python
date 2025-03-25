"""
© Ocado Group
Created on 29/01/2024 at 16:46:24(+00:00).
"""

import string
import typing as t

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.utils import IntegrityError
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from ...types import Validators
from ...validators import CharSetValidatorBuilder
from .user import User

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


class OtpBypassToken(models.Model):
    """A single use token to bypass a user's OTP authentication factor."""

    _fernet = Fernet(settings.SECRET_KEY)

    length = 8
    allowed_chars = string.ascii_lowercase
    max_count = 10
    validators: Validators = [
        MinLengthValidator(length),
        MaxLengthValidator(length),
        CharSetValidatorBuilder(
            allowed_chars,
            "lowercase alpha characters (a-z)",
        ),
    ]

    # pylint: disable-next=missing-class-docstring,too-few-public-methods
    class Manager(models.Manager["OtpBypassToken"]):
        def bulk_create(self, user: User):  # type: ignore[override]
            """Bulk create OTP-bypass tokens.

            Args:
                otp_bypass_tokens: The token values to be hashed.

            Returns:
                Many OtpBypassToken instances.
            """
            tokens: t.Set[str] = set()
            while len(tokens) < OtpBypassToken.max_count:
                tokens.add(
                    get_random_string(
                        OtpBypassToken.length,
                        OtpBypassToken.allowed_chars,
                    )
                )

            otp_bypass_tokens: t.List[OtpBypassToken] = []
            for token in tokens:
                otp_bypass_token = OtpBypassToken(
                    user=user,
                    # pylint: disable-next=protected-access
                    token=OtpBypassToken._fernet.encrypt(
                        token.encode()
                    ).decode(),
                )

                otp_bypass_tokens.append(otp_bypass_token)

            user.otp_bypass_tokens.all().delete()

            return super().bulk_create(otp_bypass_tokens)

    objects: Manager = Manager()

    user = models.ForeignKey(
        User,
        related_name="otp_bypass_tokens",
        on_delete=models.CASCADE,
    )

    token = models.CharField(
        _("token"),
        max_length=100,
        help_text=_("The encrypted equivalent of the token."),
    )

    class Meta(TypedModelMeta):
        verbose_name = _("OTP bypass token")
        verbose_name_plural = _("OTP bypass tokens")

    def save(self, *args, **kwargs):
        raise IntegrityError("Cannot create or update a single instance.")

    @property
    def decrypted_token(self):
        """The decrypted value of the token."""
        return self._fernet.decrypt(self.token).decode()

    def check_token(self, token: str):
        """Check if the token matches.

        Args:
            token: Token to check.

        Returns:
            A boolean designating if the token matches.
        """
        if self.decrypted_token == token.lower():
            self.delete()
            return True

        return False
