"""
© Ocado Group
Created on 12/01/2026 at 09:17:46(+00:00).
"""

import typing as t
from functools import cached_property

from django.core.exceptions import ValidationError
from django.db import models

from ..types import KwArgs
from .base import Model


class EncryptedTextField(models.BinaryField):
    """
    A custom BinaryField that registers itself as an encrypted field on the
    model class.
    """

    model: t.Type[Model]

    def _set_init_kwargs(self, kwargs: KwArgs):
        kwargs.setdefault("db_column", self.associated_data)

    def __init__(self, associated_data: str, **kwargs):
        if not associated_data:
            raise ValidationError(
                "Associated data cannot be empty.", code="no_associated_data"
            )
        self.associated_data = associated_data

        self._set_init_kwargs(kwargs)
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["associated_data"] = self.associated_data
        self._set_init_kwargs(kwargs)
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)

        if not cls._meta.abstract and not hasattr(cls, "ASSOCIATED_DATA"):
            raise ValidationError(
                f"Model '{cls.__module__}.{cls.__name__}' must define an"
                " ASSOCIATED_DATA attribute.",
                code="no_associated_data",
            )

        if not issubclass(cls, Model):
            raise ValidationError(
                f"{cls.__module__}.{cls.__name__} must subclass"
                f" {Model.__module__}.{Model.__name__}.",
                code="invalid_model_base_class",
            )

        # pylint: disable-next=protected-access
        encrypted_fields = cls._ENCRYPTED_FIELDS

        if self in encrypted_fields:
            raise ValidationError(
                "Encrypted field already registered.",
                code="already_registered",
            )

        if any(
            self.associated_data == field.associated_data
            for field in encrypted_fields
        ):
            raise ValidationError(
                f"Associated data '{self.associated_data}' already used in"
                " another encrypted field.",
                code="associated_data_already_used",
            )

        encrypted_fields.append(self)

    @property
    def _associated_data(self):
        """Returns the fully qualified associated data for this field."""
        return f"{self.model.ASSOCIATED_DATA}:{self.associated_data}".encode()

    @cached_property
    def getter_and_setter(self):
        """Returns a property that gets/sets the decrypted/encrypted value."""

        def decrypt_value(model: Model):
            """Decrypts a single value using the DEK and associated data."""
            ciphertext: t.Optional[bytes] = getattr(model, self.name)
            if ciphertext is None:
                return None

            return model.dek_aead.decrypt(
                ciphertext=ciphertext,
                associated_data=self._associated_data,
            ).decode()

        def encrypt_value(model: Model, plaintext: t.Optional[str]):
            """Encrypts a single value using the DEK and associated data."""
            value = (
                None
                if plaintext is None
                else model.dek_aead.encrypt(
                    plaintext=plaintext.encode(),
                    associated_data=self._associated_data,
                )
            )

            setattr(model, self.name, value)

        # Create property with getter and setter. Cast to str for mypy.
        return t.cast(str, property(fget=decrypt_value, fset=encrypt_value))

    @classmethod
    def initialize(cls, associated_data: str, *args, **kwargs):
        """Helper to create an EncryptedBinaryField and its property."""
        encrypted_text_field = cls(associated_data, *args, **kwargs)
        return encrypted_text_field, encrypted_text_field.getter_and_setter
