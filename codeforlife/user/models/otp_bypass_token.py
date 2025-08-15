"""
© Ocado Group
Created on 29/01/2024 at 16:46:24(+00:00).
"""

import string
import typing as t

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.utils import IntegrityError
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from ...models import EncryptedCharField
from ...types import Validators
from ...validators import CharSetValidatorBuilder
from .user import User

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object


class OtpBypassToken(models.Model):
    """A single use token to bypass a user's OTP authentication factor."""

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

            user.otp_bypass_tokens.all().delete()

            return super().bulk_create(
                [OtpBypassToken(user=user, token=token) for token in tokens]
            )

    objects: Manager = Manager()

    user = models.ForeignKey(
        User,
        related_name="otp_bypass_tokens",
        on_delete=models.CASCADE,
    )

    token = EncryptedCharField(
        _("token"),
        max_length=100,
        help_text=_("The encrypted equivalent of the token."),
    )

    class Meta(TypedModelMeta):
        verbose_name = _("OTP bypass token")
        verbose_name_plural = _("OTP bypass tokens")

    def save(self, *args, **kwargs):
        raise IntegrityError("Cannot create or update a single instance.")

    def check_token(self, token: str):
        """Check if the token matches.

        Args:
            token: Token to check.

        Returns:
            A boolean designating if the token matches.
        """
        if self.token == token.lower():
            self.delete()
            return True

        return False
