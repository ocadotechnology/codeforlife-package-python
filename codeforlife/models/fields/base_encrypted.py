"""
© Ocado Group
Created on 19/01/2026 at 09:57:04(+00:00).

This is where the core logic of transparent encryption and decryption happens.
`BaseEncryptedField` is a generic field that stores encrypted data as bytes. The
magic is in its descriptor, `EncryptedAttribute`.

The descriptor intercepts get and set operations:

- On `set`: The value is not immediately encrypted. It's wrapped in a
  `_PendingEncryption` object and stored in the model instance's `__dict__`.
  This is a performance optimization to avoid encrypting a value multiple
  times if it's changed repeatedly before saving. Any previously cached
  decrypted value is cleared.
- On `get`: The descriptor first checks if a decrypted value is already cached
  on the model instance. If so, it returns it immediately. Otherwise, it checks
  the value in `__dict__`. If it's ciphertext (bytes), it's decrypted
  on-the-fly, cached on the instance, and then returned. If it's a pending
  plaintext value, it's returned directly.
- On `save`: The field's `pre_save` method is called. It checks for a
  `_PendingEncryption` object. If found, it encrypts the plaintext value using
  the `dek_aead` and replaces it with the resulting ciphertext bytes, which are
  then written to the database.

A key challenge is differentiating between a value that has just been loaded
from the database (and is therefore encrypted ciphertext) and a new plaintext
value that a developer is setting.

- When a developer sets `user.email = "new@example.com"`, this is **new
  plaintext** that needs to be encrypted on save.
- When Django loads a `User` from the database, the `email` field contains
  **existing ciphertext** (raw bytes).

We solve this with two wrapper classes:

1. `_PendingEncryption(value)`: When a developer sets a value on the field, the
   `EncryptedAttribute` descriptor wraps it in this class. This marks the data
   as "dirty" or "pending encryption." The `pre_save` method looks for this
   wrapper to know what needs to be encrypted.
2. `_TrustedCiphertext(value)`: When Django loads data from the database, the
   `from_db_value` method on the field is called. We wrap the raw bytes from the
   database in this class. The `EncryptedAttribute` descriptor's `__set__`
   method sees this wrapper and knows the value is already-encrypted ciphertext,
   preventing it from being re-wrapped as `_PendingEncryption`. This avoids
   unnecessary re-encryption of data that hasn't changed.

This distinction allows the field to correctly handle both new data and existing
data without ambiguity.
"""

import typing as t
from dataclasses import dataclass
from enum import IntEnum, auto

from django.core.exceptions import ValidationError
from django.db.models import BinaryField

from ...types import Args, KwArgs
from ..encrypted import EncryptedModel
from ..utils import is_real_model_class
from .deferred_attribute import DeferredAttribute

T = t.TypeVar("T")
Ciphertext: t.TypeAlias = t.Union[bytes, memoryview]


@dataclass(frozen=True)
class _PendingEncryption(t.Generic[T]):
    """A wrapper for plaintext that is pending encryption."""

    value: T


@dataclass(frozen=True)
class _TrustedCiphertext:
    """A wrapper for ciphertext that comes directly from the database."""

    class Source(IntEnum):
        """The source of the ciphertext."""

        DB = auto()
        FIXTURE = auto()

    ciphertext: Ciphertext
    source: Source


Value: t.TypeAlias = t.Union[_TrustedCiphertext, _PendingEncryption[T]]

AnyBaseEncryptedField = t.TypeVar(
    "AnyBaseEncryptedField", bound="BaseEncryptedField"
)


class EncryptedAttribute(
    DeferredAttribute[EncryptedModel, AnyBaseEncryptedField, Value[T]],
    t.Generic[AnyBaseEncryptedField, T],
):
    """
    Descriptor that handles the get/set mechanics for encrypted fields.
    """

    def __get__(self, instance, cls=None):
        # Get the internal value from the instance.
        internal_value = super().__get__(instance, cls)

        # Return the descriptor itself when accessed on the class.
        if internal_value is self:
            return self

        # No data to decrypt.
        if internal_value is None:
            return None

        # The user just set this value, return it directly.
        if isinstance(internal_value, _PendingEncryption):
            return internal_value.value

        if isinstance(internal_value, _TrustedCiphertext):
            # If the ciphertext came from a fixture, do not decrypt it so that
            # it can be loaded as-is into the database.
            if internal_value.source == _TrustedCiphertext.Source.FIXTURE:
                return internal_value.ciphertext

            # If we have a cached decrypted value, return it.
            if self.field.attname in instance.__decrypted_values__:
                return t.cast(
                    T, instance.__decrypted_values__[self.field.attname]
                )

            # Decrypt the value before returning it.
            decrypted_value = t.cast(
                T,
                self.field.decrypt_value(
                    instance, bytes(internal_value.ciphertext)
                ),
            )

            # Cache the decrypted value on the instance.
            instance.__decrypted_values__[self.field.attname] = decrypted_value

            return decrypted_value

        raise ValidationError(
            "Unexpected internal value type for encrypted field.",
            code="invalid_internal_value_type",
        )

    def __set__(
        self,
        instance,
        value: t.Optional[  # type: ignore[override]
            t.Union[memoryview, _TrustedCiphertext, T]
        ],
    ):
        # Clear any cached decrypted value.
        instance.__decrypted_values__.pop(self.field.attname, None)

        # Determine the internal value to set.
        internal_value: t.Optional[Value[T]]
        if value is None:
            internal_value = None
        elif isinstance(value, memoryview):  # From fixture.
            if not isinstance(value.obj, bytes):
                raise ValidationError(
                    "Expected bytes in memoryview for encrypted field.",
                    code="invalid_memoryview_type",
                )
            internal_value = _TrustedCiphertext(
                value, _TrustedCiphertext.Source.FIXTURE
            )
        elif isinstance(value, _TrustedCiphertext):  # From DB.
            internal_value = value
        else:  # From user input.
            internal_value = _PendingEncryption(value)

        # Set the internal value on the instance.
        super().__set__(instance, internal_value)


class BaseEncryptedField(BinaryField, t.Generic[T]):
    """Encrypted field base class."""

    model: t.Type[EncryptedModel]

    descriptor_class = EncryptedAttribute

    # --------------------------------------------------------------------------
    # Construction & Deconstruction
    # --------------------------------------------------------------------------

    def __init__(self, associated_data: str, **kwargs):
        if not associated_data:
            raise ValidationError(
                "Associated data cannot be empty.",
                code="no_associated_data",
            )
        self.associated_data = associated_data

        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = t.cast(
            t.Tuple[str, str, Args, KwArgs], super().deconstruct()
        )

        kwargs["associated_data"] = self.associated_data

        return name, path, args, kwargs

    # --------------------------------------------------------------------------
    # Django Model Field Integration
    # --------------------------------------------------------------------------

    def contribute_to_class(self, cls, name, private_only=False):
        """
        Called by Django when the field is added to a model. This method
        performs critical validations and registers the field with the model.
        """
        super().contribute_to_class(cls, name, private_only)

        # Skip non-real models.
        if not is_real_model_class(cls):
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

    @t.overload  # type: ignore[override]
    def __get__(  # Get the descriptor with the correct types.
        self, instance: None, owner: t.Any
    ) -> EncryptedAttribute[t.Self, T]: ...

    @t.overload
    def __get__(  # Get the internal value when accessed on an instance.
        self, instance: EncryptedModel, owner: t.Any
    ) -> t.Optional[T]: ...

    # Actual implementation of __get__.
    def __get__(self, instance: t.Optional[EncryptedModel], owner: t.Any):
        return t.cast(
            t.Union[EncryptedAttribute[t.Self, T], t.Optional[T]],
            # pylint: disable-next=no-member
            super().__get__(instance, owner),
        )

    # Set the internal value when assigned on an instance.
    def __set__(self, instance: EncryptedModel, value: t.Optional[T]): ...

    def from_db_value(self, value: t.Optional[Ciphertext], _, __):
        """
        Converts a value as returned by the database to a Python object.
        We wrap the raw bytes in _TrustedCiphertext to signal that this is
        existing ciphertext from the database, not new plaintext.
        """
        if value is None:
            return None

        # Wrap it so __set__ knows this is NOT new user input.
        return _TrustedCiphertext(value, _TrustedCiphertext.Source.DB)

    def pre_save(
        self, model_instance: EncryptedModel, add  # type: ignore[override]
    ):
        """Before saving, encrypt any pending values."""
        value: t.Optional[Value[T]] = model_instance.__dict__.get(self.attname)

        # No data to encrypt.
        if value is None:
            return None

        # Data needs encrypting.
        if isinstance(value, _PendingEncryption):
            return self.encrypt_value(model_instance, value.value)

        # Already encrypted data from DB, store as-is.
        if isinstance(value, _TrustedCiphertext):
            return value.ciphertext

        raise ValidationError(
            f"Unexpected value type '{type(value)}' for encryption.",
            code="invalid_value_type",
        )

    # --------------------------------------------------------------------------
    # Crypto Logic
    # --------------------------------------------------------------------------

    def bytes_to_value(self, data: bytes) -> T:
        """
        Subclasses must implement this method to convert decrypted bytes back to
        the field's value type.
        """
        raise NotImplementedError()

    def value_to_bytes(self, value: T) -> bytes:
        """
        Subclasses must implement this method to convert the field's value to
        bytes before encryption.
        """
        raise NotImplementedError()

    @property
    def full_associated_data(self):
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
            associated_data=self.full_associated_data,
        )

        return self.bytes_to_value(data)

    def encrypt_value(self, instance: EncryptedModel, plaintext: t.Optional[T]):
        """Encrypts a single value using the DEK and associated data."""
        return (
            None
            if plaintext is None
            else instance.dek_aead.encrypt(
                plaintext=self.value_to_bytes(plaintext),
                associated_data=self.full_associated_data,
            )
        )
