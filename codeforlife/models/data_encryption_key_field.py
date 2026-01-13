import typing as t
from functools import cached_property
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import SimpleLazyObject
from django.utils.translation import gettext_lazy as _
from tink import (  # type: ignore[import-untyped]
    BinaryKeysetReader,
    BinaryKeysetWriter,
    new_keyset_handle,
    read_keyset_handle,
)
from tink.aead import Aead, aead_key_templates  # type: ignore[import-untyped]
from tink.integration.gcpkms import GcpKmsClient  # type: ignore[import-untyped]

from ..models import Model
from ..types import KwArgs


class DataEncryptionKeyField(models.BinaryField):
    """
    A custom BinaryField to store a encrypted data encryption key (DEK).
    """

    _master_key_aead: Aead = SimpleLazyObject(
        lambda: GcpKmsClient(
            settings.KMS_MASTER_KEY_URI, settings.KMS_CREDENTIALS_PATH
        ).get_aead(settings.KMS_MASTER_KEY_URI)
    )

    default_verbose_name = "data encryption key"
    default_help_text = (
        "The encrypted data encryption key (DEK) for this model."
    )

    @classmethod
    def _set_init_kwargs(cls, kwargs: KwArgs):
        kwargs["editable"] = False
        kwargs["default"] = cls.create_dek
        kwargs.setdefault("verbose_name", _(cls.default_verbose_name))
        kwargs.setdefault("help_text", _(cls.default_help_text))

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

        self._set_init_kwargs(kwargs)
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        self._set_init_kwargs(kwargs)
        return name, path, args, kwargs

    # TODO: inherit EncryptedBinaryField
    # def contribute_to_class(self, cls, name, private_only=False):
    #     super().contribute_to_class(cls, name, private_only)

    @classmethod
    def create_dek(cls):
        """
        Generates a new random AES-256-GCM key, wraps it with Cloud KMS,
        and returns the binary blob for storage.
        """
        stream = BytesIO()
        new_keyset_handle(key_template=aead_key_templates.AES256_GCM).write(
            keyset_writer=BinaryKeysetWriter(stream),
            master_key_primitive=cls._master_key_aead,
        )
        return stream.getvalue()

    @cached_property
    def aead(self):
        """Return the AEAD primitive for this data encryption key."""

        def get_aead(model: Model):
            dek: t.Optional[bytes] = getattr(model, self.name, None)
            if not dek:
                raise ValueError("The data encryption key (DEK) is missing.")

            # dek  # TODO: Cache this value.

            return read_keyset_handle(
                keyset_reader=BinaryKeysetReader(dek),
                master_key_aead=self._master_key_aead,
            ).primitive(Aead)

        # Create a property with getter. Cast to Aead for mypy.
        return t.cast(Aead, property(fget=get_aead))

    @classmethod
    def initialize(cls, **kwargs):
        """Helpers to create a new DEK and return its AEAD primitive."""
        dek = cls(**kwargs)
        return dek, dek.aead
