import typing as t
from functools import cached_property

from django.core.exceptions import ValidationError
from django.db import models

from ..types import Args, KwArgs
from .encrypted import EncryptedModel

T = t.TypeVar("T")


class BaseEncryptedField(models.BinaryField, t.Generic[T]):
    """Encrypted field base class."""

    model: t.Type[EncryptedModel]

    # Whether to allows decrypting/encrypting the value via the property.
    decrypt_value = True
    encrypt_value = True

    def set_init_kwargs(self, kwargs: KwArgs):
        """Sets common init kwargs."""
        kwargs.setdefault("db_column", self.associated_data)

    def __init__(self, associated_data: str, **kwargs):
        if not associated_data:
            raise ValidationError(
                "Associated data cannot be empty.",
                code="no_associated_data",
            )
        self.associated_data = associated_data

        self.set_init_kwargs(kwargs)
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = t.cast(
            t.Tuple[str, str, Args, KwArgs], super().deconstruct()
        )

        self.set_init_kwargs(kwargs)
        kwargs["associated_data"] = self.associated_data

        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)

        # Skip fake models used for migrations.
        if cls.__module__ == "__fake__":
            return

        # Ensure the model subclasses EncryptedModel.
        if not issubclass(cls, EncryptedModel):
            raise ValidationError(
                f"'{cls.__module__}.{cls.__name__}' must subclass"
                f" '{EncryptedModel.__module__}.{EncryptedModel.__name__}'.",
                code="invalid_model_base_class",
            )

        # Ensure the model defines associated_data correctly.
        if not cls._meta.abstract:
            if not hasattr(cls, "associated_data"):
                raise ValidationError(
                    f"'{cls.__module__}.{cls.__name__}' must define an"
                    " associated_data attribute.",
                    code="no_associated_data",
                )

            if not isinstance(cls.associated_data, str):
                raise ValidationError(
                    f"'{cls.__module__}.{cls.__name__}.associated_data' must be"
                    " a string.",
                    code="invalid_associated_data_type",
                )

            if not cls.associated_data:
                raise ValidationError(
                    f"'{cls.__module__}.{cls.__name__}.associated_data' cannot"
                    " be empty.",
                    code="empty_associated_data",
                )

        # Ensure no duplicate encrypted fields.
        if self in cls.ENCRYPTED_FIELDS:
            raise ValidationError(
                "Encrypted field already registered.",
                code="already_registered",
            )

        # Ensure no duplicate associated data.
        for field in cls.ENCRYPTED_FIELDS:
            if self.associated_data == field.associated_data:
                raise ValidationError(
                    f"The encrypted fields '{self.name}' and '{field.name}'"
                    " have the same associated data.",
                    code="associated_data_already_used",
                )

        # Register this field as an encrypted field on the model.
        cls.ENCRYPTED_FIELDS.append(self)

    def bytes_to_value(self, data: bytes) -> T:
        """Converts decrypted bytes to the field value."""
        raise NotImplementedError()

    def value_to_bytes(self, value: T) -> bytes:
        """Converts the field value to bytes for encryption."""
        raise NotImplementedError()

    @property
    def _associated_data(self):
        """Returns the fully qualified associated data for this field."""
        return f"{self.model.associated_data}:{self.associated_data}".encode()

    @cached_property
    def value(self):
        """Returns a property that gets/sets the decrypted/encrypted value."""

        def decrypt_value(model: EncryptedModel):
            """Decrypts a single value using the DEK and associated data."""
            ciphertext: t.Optional[bytes] = getattr(model, self.name)
            if ciphertext is None:
                return None

            data = model.dek_aead.decrypt(
                ciphertext=ciphertext,
                associated_data=self._associated_data,
            )

            return self.bytes_to_value(data)

        def encrypt_value(model: EncryptedModel, plaintext: t.Optional[T]):
            """Encrypts a single value using the DEK and associated data."""
            value = (
                None
                if plaintext is None
                else model.dek_aead.encrypt(
                    plaintext=self.value_to_bytes(plaintext),
                    associated_data=self._associated_data,
                )
            )

            setattr(model, self.name, value)

        # Create property with getter and/or setter.
        value = property(
            fget=decrypt_value if self.decrypt_value else None,
            fset=encrypt_value if self.encrypt_value else None,
        )

        return t.cast(T, value)  # Cast to T for mypy.

    @classmethod
    def initialize(cls, associated_data: str, **kwargs):
        """Helper to create an encrypted field and its value-property."""
        encrypted_field = cls(associated_data=associated_data, **kwargs)
        return encrypted_field, encrypted_field.value
