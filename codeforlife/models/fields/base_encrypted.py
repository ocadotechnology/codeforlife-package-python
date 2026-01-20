"""
© Ocado Group
Created on 19/01/2026 at 09:57:04(+00:00).
"""

import typing as t
from dataclasses import dataclass
from functools import cached_property

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query_utils import DeferredAttribute

from ...types import Args, KwArgs
from ..encrypted import EncryptedModel

T = t.TypeVar("T")
Default: t.TypeAlias = t.Union[T, t.Callable[[], T]]


@dataclass(frozen=True)
class _PendingEncryption(t.Generic[T]):
    """Helper: Data waiting to be encrypted (User Input)."""

    value: T
    instance: EncryptedModel


@dataclass(frozen=True)
class _TrustedCiphertext:
    """Helper: Trusted ciphertext directly from the DB."""

    ciphertext: bytes


AnyBaseEncryptedField = t.TypeVar(
    "AnyBaseEncryptedField", bound="BaseEncryptedField"
)


class EncryptedAttribute(DeferredAttribute, t.Generic[AnyBaseEncryptedField]):
    """
    Custom descriptor that handles the get/set mechanics for encrypted fields.
    """

    field: AnyBaseEncryptedField

    @property
    def _field(self):
        return t.cast(AnyBaseEncryptedField, self.field)

    def __get__(self, instance: t.Optional[EncryptedModel], cls=None):
        # Return the descriptor itself when accessed on the class.
        if instance is None:
            return self

        # If we have a cached decrypted value, return it.
        cache_name = self._field.cache_name
        if hasattr(instance, cache_name):
            return getattr(instance, cache_name)

        # Get the raw data from the instance.
        value = t.cast(
            t.Optional[bytes | _PendingEncryption],
            super().__get__(instance, cls),  # type: ignore[misc]
        )

        # No data to decrypt.
        if value is None:
            return None

        # The user just set this value, return it directly.
        if isinstance(value, _PendingEncryption):
            return value.value

        # Decrypt the value before returning it.
        decrypted_value = self._field.decrypt_value(instance, value)

        # Cache the decrypted value on the instance.
        setattr(instance, cache_name, decrypted_value)

        return decrypted_value

    def __set__(
        self,
        instance: EncryptedModel,
        value: t.Optional[t.Union[T, _TrustedCiphertext]],
    ):
        # Clear any cached decrypted value.
        cache_name = self._field.cache_name
        if hasattr(instance, cache_name):
            delattr(instance, cache_name)

        # Store the internal value on the instance.
        instance.__dict__[self._field.attname] = (
            None
            if value is None
            else (
                # If it's trusted ciphertext from the DB, store it directly.
                value.ciphertext
                if isinstance(value, _TrustedCiphertext)
                # If it's a new value from the user, store a pending encryption.
                else _PendingEncryption(value, instance)
            )
        )


class BaseEncryptedField(models.BinaryField, t.Generic[T]):
    """Encrypted field base class."""

    model: t.Type[EncryptedModel]

    descriptor_class = EncryptedAttribute

    # --------------------------------------------------------------------------
    # Construction & Deconstruction
    # --------------------------------------------------------------------------

    def set_init_kwargs(self, kwargs: KwArgs):
        """Sets common init kwargs."""
        kwargs.setdefault("db_column", self.associated_data)

    def __init__(
        self,
        associated_data: str,
        default: t.Optional[Default[T]] = None,
        **kwargs,
    ):
        if not associated_data:
            raise ValidationError(
                "Associated data cannot be empty.",
                code="no_associated_data",
            )
        self.associated_data = associated_data

        self.set_init_kwargs(kwargs)
        super().__init__(**kwargs, default=default)

    def deconstruct(self):
        name, path, args, kwargs = t.cast(
            t.Tuple[str, str, Args, KwArgs], super().deconstruct()
        )

        self.set_init_kwargs(kwargs)
        kwargs["associated_data"] = self.associated_data

        return name, path, args, kwargs

    # --------------------------------------------------------------------------
    # Django Model Field Integration
    # --------------------------------------------------------------------------

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

    # --------------------------------------------------------------------------
    # Descriptor Methods
    # --------------------------------------------------------------------------

    @t.overload  # type: ignore[no-overload-impl,override]
    def __get__(
        self, instance: None, owner: t.Any
    ) -> EncryptedAttribute[t.Self]: ...

    @t.overload
    def __get__(
        self, instance: EncryptedModel, owner: t.Any
    ) -> t.Optional[T]: ...

    @cached_property
    def cache_name(self):
        """The name used to cache the decrypted value on the instance."""
        return f"_{self.name}_decrypted_value"

    # pylint: disable-next=unused-argument
    def from_db_value(self, value: t.Optional[bytes], expression, connection):
        """
        Converts a value as returned by the database to a Python object. It is
        the reverse of get_prep_value().

        https://docs.djangoproject.com/en/5.1/howto/custom-model-fields/#converting-values-to-python-objects
        """
        if value is None:
            return None

        # Wrap it so __set__ knows this is NOT new user input.
        return _TrustedCiphertext(value)

    def get_prep_value(self, value: t.Optional[_PendingEncryption[T]]):
        """
        'value' is the current value of the model's attribute, and the method
        should return data in a format that has been prepared for use as a
        parameter in a query.

        https://docs.djangoproject.com/en/5.1/howto/custom-model-fields/#converting-python-objects-to-query-values
        """
        # If it's a pending encryption, encrypt it now.
        if isinstance(value, _PendingEncryption):
            return self.encrypt_value(value.instance, value.value)

        # If it's already bytes (e.g. strict assignment), pass through.
        return super().get_prep_value(value)

    # --------------------------------------------------------------------------
    # Crypto Logic
    # --------------------------------------------------------------------------

    def bytes_to_value(self, data: bytes) -> T:
        """Converts decrypted bytes to the field value."""
        raise NotImplementedError()

    def value_to_bytes(self, value: T) -> bytes:
        """Converts the field value to bytes for encryption."""
        raise NotImplementedError()

    @property
    def qual_associated_data(self):
        """Returns the fully qualified associated data for this field."""
        return f"{self.model.associated_data}:{self.associated_data}".encode()

    def decrypt_value(
        self, instance: EncryptedModel, ciphertext: t.Optional[bytes]
    ):
        """Decrypts a single value using the DEK and associated data."""
        if ciphertext is None:
            return None

        data = instance.dek_aead.decrypt(
            ciphertext=ciphertext,
            associated_data=self.qual_associated_data,
        )

        return self.bytes_to_value(data)

    def encrypt_value(self, instance: EncryptedModel, plaintext: t.Optional[T]):
        """Encrypts a single value using the DEK and associated data."""
        return (
            None
            if plaintext is None
            else instance.dek_aead.encrypt(
                plaintext=self.value_to_bytes(plaintext),
                associated_data=self.qual_associated_data,
            )
        )
