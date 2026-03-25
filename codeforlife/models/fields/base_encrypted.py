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

from django.core.exceptions import ValidationError
from django.db.models import BinaryField

from ...types import Args, KwArgs
from ..encrypted import EncryptedModel
from ..utils import is_real_model_class
from .deferred_attribute import DeferredAttribute

T = t.TypeVar("T")
Ciphertext: t.TypeAlias = t.Union[bytes, memoryview]
AnyBaseEncryptedField = t.TypeVar(
    "AnyBaseEncryptedField", bound="BaseEncryptedField"
)


class EncryptedAttribute(
    DeferredAttribute[AnyBaseEncryptedField, EncryptedModel, Ciphertext],
    t.Generic[AnyBaseEncryptedField],
):
    """Descriptor that handles clearing cached decrypted values."""

    def __set__(self, instance, value):
        # Clear any cached decrypted value.
        instance.__decrypted_values__.pop(self.field.attname, None)

        # Set the internal value on the instance.
        super().__set__(instance, value)


class BaseEncryptedField(BinaryField, t.Generic[T]):
    """Encrypted field base class."""

    model: t.Type[EncryptedModel]

    descriptor_class = EncryptedAttribute

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

    @t.overload  # type: ignore[override]
    def __get__(  # Get the descriptor.
        self, instance: None, owner: t.Any
    ) -> EncryptedAttribute[t.Self]: ...

    @t.overload
    def __get__(  # Get the value.
        self, instance: EncryptedModel, owner: t.Any
    ) -> t.Optional[Ciphertext]: ...

    # Actual implementation of __get__.
    def __get__(self, instance: t.Optional[EncryptedModel], owner: t.Any):
        return t.cast(
            t.Union[EncryptedAttribute[t.Self], t.Optional[Ciphertext]],
            # pylint: disable-next=no-member
            super().__get__(instance, owner),
        )

    def __set__(  # Set the value.
        self, instance: EncryptedModel, value: t.Optional[Ciphertext]
    ): ...

    def value_from_object(self, obj):
        return t.cast(t.Optional[Ciphertext], super().value_from_object(obj))

    def pre_save(
        self, model_instance: EncryptedModel, add  # type: ignore[override]
    ):
        """Before saving, encrypt any pending values."""

        # Data needs encrypting.
        if self.attname in model_instance.__pending_encryption_values__:
            value = t.cast(
                T,
                model_instance.__pending_encryption_values__.pop(self.attname),
            )
            return self._encrypt(model_instance, value)

        # If data is already encrypted or None, return it as-is.
        return super().pre_save(model_instance, add)

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

    def _decrypt(self, instance: EncryptedModel, ciphertext: bytes):
        """Decrypts a single value using the DEK and associated data."""
        data = instance.dek_aead.decrypt(
            ciphertext=ciphertext,
            associated_data=self.full_associated_data,
        )

        return self.bytes_to_value(data)

    def _encrypt(self, instance: EncryptedModel, plaintext: T):
        """Encrypts a single value using the DEK and associated data."""
        return instance.dek_aead.encrypt(
            plaintext=self.value_to_bytes(plaintext),
            associated_data=self.full_associated_data,
        )

    @staticmethod
    def get(instance: EncryptedModel, field_name: str):
        """Convenience method to get the decrypted value of an encrypted field.

        Args:
            instance: The model instance from which to decrypt the value.
            field_name: The name of the encrypted field to decrypt.

        Returns:
            The decrypted plaintext value, or None if the field is empty.
        """
        field = t.cast(
            BaseEncryptedField[T], instance._meta.get_field(field_name)
        )

        # If we have a cached pending encryption value, return it.
        if field.attname in instance.__pending_encryption_values__:
            return t.cast(
                T, instance.__pending_encryption_values__[field.attname]
            )

        # If we have a cached decrypted value, return it.
        if field.attname in instance.__decrypted_values__:
            return t.cast(T, instance.__decrypted_values__[field.attname])

        # Get the internal value from the instance's __dict__.
        value = field.value_from_object(instance)
        if value is None:
            return None

        # Decrypt the value before returning it.
        # pylint: disable-next=protected-access
        decrypted_value = field._decrypt(instance, bytes(value))

        # Cache the decrypted value on the instance.
        instance.__decrypted_values__[field.attname] = decrypted_value

        return decrypted_value

    @staticmethod
    def set(instance: EncryptedModel, value: t.Optional[T], field_name: str):
        """Convenience method to set a value for an encrypted field.

        If the field's decrypted value is already cached on the instance, this
        method will clear the cache since the value is changing. If not None,
        the new value will be set as pending encryption to indicate it needs
        encryption on save.

        Args:
            instance: The model instance on which to set the value.
            value: The plaintext value to set. If None, the field is cleared.
            field_name: The name of the encrypted field to set.
        """
        field = t.cast(
            BaseEncryptedField[T], instance._meta.get_field(field_name)
        )

        # Set the pending encryption value.
        if value is None:
            instance.__pending_encryption_values__.pop(field.attname, None)
        else:
            instance.__pending_encryption_values__[field.attname] = value

        # In all cases we need to clear the internal and cached-decrypted value.
        setattr(instance, field_name, None)
