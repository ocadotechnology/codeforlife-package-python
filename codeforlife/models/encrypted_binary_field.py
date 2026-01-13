"""
© Ocado Group
Created on 12/01/2026 at 09:17:46(+00:00).
"""

import typing as t
from functools import cached_property

from django.core.exceptions import ValidationError
from django.db import models

from ..models import DataEncryptionKeyModel, Model


class EncryptedBinaryField(models.BinaryField):
    """
    A custom BinaryField that registers itself as an encrypted field on the
    model class.
    """

    model: t.Type[Model]

    def __init__(self, associated_data: str, *args, **kwargs):
        if not associated_data:
            raise ValidationError(
                "Associated data cannot be empty.", code="no_associated_data"
            )
        self.associated_data = associated_data

        # Set db_column to associated_data by default.
        kwargs.setdefault("db_column", associated_data)

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["associated_data"] = self.associated_data
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

    @cached_property
    def getter_and_setter(self):
        """Returns a property that gets/sets the decrypted/encrypted value."""
        field = self

        def to_associated_data(model: Model, dek_model: DataEncryptionKeyModel):
            """Generates the Associated Data (AD) for encryption/decryption."""
            return ":".join(
                [
                    dek_model.ASSOCIATED_DATA,
                    dek_model.pk,
                    model.ASSOCIATED_DATA,
                    field.associated_data,
                ]
            ).encode()

        def decrypt_value(self: Model):
            """Decrypts a single value using the DEK and associated data."""
            ciphertext: t.Optional[bytes] = getattr(self, field.name)
            if ciphertext is None:
                return None

            dek_model = self.get_data_encryption_key_model()
            return dek_model.data_key_aead.decrypt(
                ciphertext=ciphertext,
                associated_data=to_associated_data(self, dek_model),
            ).decode()

        def encrypt_value(self: Model, plaintext: t.Optional[str]):
            """Encrypts a single value using the DEK and associated data."""
            if plaintext is None:
                value = None
            else:
                dek_model = self.get_data_encryption_key_model()
                value = dek_model.data_key_aead.encrypt(
                    plaintext=plaintext.encode(),
                    associated_data=to_associated_data(self, dek_model),
                )

            setattr(self, field.name, value)

        # Create property with getter and setter. Cast to str for mypy.
        return t.cast(str, property(fget=decrypt_value, fset=encrypt_value))

    @classmethod
    def initialize(cls, associated_data: str, *args, **kwargs):
        """Helper to create an EncryptedBinaryField and its property."""
        encrypted_binary_field = cls(associated_data, *args, **kwargs)
        return encrypted_binary_field, encrypted_binary_field.getter_and_setter
