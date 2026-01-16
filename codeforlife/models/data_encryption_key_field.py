import typing as t
from functools import cached_property

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from ..encryption import create_dek, get_dek_aead
from ..models import Model
from ..types import KwArgs

if t.TYPE_CHECKING:
    from tink.aead import Aead  # type: ignore[import-untyped]


class DataEncryptionKeyField(models.BinaryField):
    """
    A custom BinaryField to store a encrypted data encryption key (DEK).
    """

    default_verbose_name = "data encryption key"
    default_help_text = (
        "The encrypted data encryption key (DEK) for this model."
    )

    def set_init_kwargs(self, kwargs: KwArgs):
        """Sets common init kwargs."""
        kwargs["editable"] = False
        kwargs["default"] = create_dek
        kwargs.setdefault("verbose_name", _(self.default_verbose_name))
        kwargs.setdefault("help_text", _(self.default_help_text))

    def __init__(self, **kwargs):
        if kwargs.get("editable", False):
            raise ValidationError(
                "DataEncryptionKeyField cannot be editable.",
                code="editable_not_allowed",
            )
        if "default" in kwargs:
            raise ValidationError(
                "DataEncryptionKeyField cannot have a default value.",
                code="default_not_allowed",
            )
        if kwargs.get("null", False):
            raise ValidationError(
                "DataEncryptionKeyField cannot be null.",
                code="null_not_allowed",
            )

        self.set_init_kwargs(kwargs)
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        self.set_init_kwargs(kwargs)
        return name, path, args, kwargs

    @cached_property
    def aead(self):
        """Return the AEAD primitive for this data encryption key."""

        def get_aead(model: Model):
            dek: bytes = getattr(model, self.name)

            # TODO: Cache this value.
            return get_dek_aead(dek)

        # Create a property with getter. Cast to Aead for mypy.
        return t.cast("Aead", property(fget=get_aead))

    @classmethod
    def initialize(cls, **kwargs):
        """Helpers to create a new DEK and return its AEAD primitive."""
        dek = cls(**kwargs)
        return dek, dek.aead
