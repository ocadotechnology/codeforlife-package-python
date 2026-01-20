"""
© Ocado Group
Created on 19/01/2026 at 09:56:57(+00:00).
"""

import typing as t
from functools import cached_property
from unittest.mock import MagicMock

from django.db import models

from ...encryption import FakeAead
from ...tests import TestCase
from ..encrypted import EncryptedModel
from .base_encrypted import (
    BaseEncryptedField,
    _PendingEncryption,
    _TrustedCiphertext,
)

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes


class FakeEncryptedModel(EncryptedModel):
    """A fake EncryptedModel for testing."""

    associated_data = "model"

    class Meta(TypedModelMeta):
        abstract = True

    @cached_property
    def dek_aead(self):
        return FakeAead.as_mock()


class FakeModelMeta(TypedModelMeta):
    """A fake Meta class for testing."""

    app_label = "codeforlife.user"


# pylint: disable-next=abstract-method
class FakeEncryptedField(BaseEncryptedField[str]):
    """A fake BaseEncryptedField for testing."""

    value_to_bytes: MagicMock
    bytes_to_value: MagicMock

    @staticmethod
    def _value_to_bytes(value: str):
        return value.encode()

    @staticmethod
    def _bytes_to_value(data: bytes):
        return data.decode()

    def __init__(self, associated_data, default=None, **kwargs):
        super().__init__(associated_data, default, **kwargs)

        self.value_to_bytes = MagicMock(side_effect=self._value_to_bytes)
        self.bytes_to_value = MagicMock(side_effect=self._bytes_to_value)


class EncryptedModelTestCase(TestCase):

    @staticmethod
    def value_to_bytes(value: str):
        """Converts a string value to bytes."""
        return value.encode()

    @staticmethod
    def bytes_to_value(data: bytes):
        """Converts bytes data to a string value."""
        return data.decode()

    def setUp(self):
        # Set up the first field with a non-callable default for testing.
        self.field_associated_data = "field"
        self.field_default = "default"
        self.field_encrypted_default = FakeAead.encrypt(
            self.value_to_bytes(self.field_default)
        )
        self.field_decrypted_default = FakeAead.decrypt(
            self.field_encrypted_default
        )
        self.field = FakeEncryptedField(
            associated_data=self.field_associated_data,
            default=self.field_default,
        )

        # Set up a second field with a callable default for testing.
        self.field2_associated_data = "field2"
        self.field2_default = "default2"
        self.field2 = FakeEncryptedField(
            associated_data=self.field2_associated_data,
            default=lambda: self.field2_default,
        )

    def test_init__no_associated_data(self):
        """Cannot create BaseEncryptedField with no associated data."""
        with self.assert_raises_validation_error(code="no_associated_data"):
            BaseEncryptedField(associated_data="")

    def test_init(self):
        """BaseEncryptedField is constructed correctly."""
        assert self.field.associated_data == self.field_associated_data
        assert self.field.db_column == self.field_associated_data

    def test_deconstruct(self):
        """BaseEncryptedField is deconstructed correctly."""
        _, _, _, kwargs = self.field.deconstruct()

        assert kwargs["associated_data"] == self.field_associated_data
        assert kwargs["db_column"] == self.field_associated_data

    def test_contribute_to_class__invalid_model_base_class(self):
        """Cannot contribute BaseEncryptedField to invalid model base class."""
        with self.assert_raises_validation_error(
            code="invalid_model_base_class"
        ):
            # pylint: disable-next=unused-variable
            class Model(models.Model):
                field = self.field

                Meta = FakeModelMeta

    def test_contribute_to_class__already_registered(self):
        """Cannot contribute BaseEncryptedField that is already registered."""
        with self.assert_raises_validation_error(code="already_registered"):
            # pylint: disable-next=unused-variable
            class Model(FakeEncryptedModel):
                field = self.field
                field2 = self.field

                Meta = FakeModelMeta

    def test_contribute_to_class(self):
        """BaseEncryptedField is contributed to class correctly."""

        class Model(FakeEncryptedModel):
            field = self.field

            Meta = FakeModelMeta

        assert self.field in Model.ENCRYPTED_FIELDS

    def test_contribute_to_class__associated_data_already_used(self):
        """
        Cannot contribute BaseEncryptedField with duplicate associated data.
        """
        with self.assert_raises_validation_error(
            code="associated_data_already_used"
        ):
            # pylint: disable-next=unused-variable
            class Model(FakeEncryptedModel):
                field = self.field
                field2 = FakeEncryptedField(
                    associated_data=self.field_associated_data
                )

                Meta = FakeModelMeta

    def test_bytes_to_value(self):
        """bytes_to_value raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            # pylint: disable-next=expression-not-assigned
            self.field.bytes_to_value(b"data")

    def test_value_to_bytes(self):
        """value_to_bytes raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            # pylint: disable-next=expression-not-assigned
            self.field.value_to_bytes("value")

    def test_qual_associated_data(self):
        """qual_associated_data returns fully qualified associated data."""

        class Model(FakeEncryptedModel):
            field = self.field

            Meta = FakeModelMeta

        assert (
            self.field.qual_associated_data
            == f"{Model.associated_data}:{self.field_associated_data}".encode()
        )

    def test_decrypt_value(self):
        """decrypt_value decrypts the given ciphertext."""

        class Model(FakeEncryptedModel):
            field = self.field

            Meta = FakeModelMeta

        # Create instance and mock shorthands.
        instance = Model()
        decrypt_mock: MagicMock = instance.dek_aead.decrypt
        bytes_to_value_mock: MagicMock = self.field.bytes_to_value

        # When ciphertext is None, no decryption occurs.
        decrypted_value = self.field.decrypt_value(instance, ciphertext=None)
        assert decrypted_value is None
        decrypt_mock.assert_not_called()
        bytes_to_value_mock.assert_not_called()

        # When ciphertext is provided, decryption occurs.
        ciphertext = self.field_encrypted_default
        decrypted_value = self.field.decrypt_value(instance, ciphertext)
        decrypt_kwargs = {
            "ciphertext": ciphertext,
            "associated_data": self.field.qual_associated_data,
        }
        decrypt_mock.assert_called_once_with(**decrypt_kwargs)
        decrypted_bytes = decrypt_mock.side_effect(**decrypt_kwargs)
        bytes_to_value_mock.assert_called_once_with(decrypted_bytes)
        assert decrypted_value == bytes_to_value_mock.side_effect(
            decrypted_bytes
        )

    def test_encrypt_value(self):
        """encrypt_value encrypts the given plaintext."""

        class Model(FakeEncryptedModel):
            field = self.field

            Meta = FakeModelMeta

        # Create instance and mock shorthands.
        instance = Model()
        encrypt_mock: MagicMock = instance.dek_aead.encrypt
        value_to_bytes_mock: MagicMock = self.field.value_to_bytes

        # When plaintext is None, no encryption occurs.
        encrypted_bytes = self.field.encrypt_value(instance, plaintext=None)
        assert encrypted_bytes is None
        value_to_bytes_mock.assert_not_called()
        encrypt_mock.assert_not_called()

        # When plaintext is provided, encryption occurs.
        plaintext = self.field_default
        encrypted_bytes = self.field.encrypt_value(instance, plaintext)
        value_to_bytes_mock.assert_called_once_with(plaintext)
        decrypted_bytes = value_to_bytes_mock.side_effect(plaintext)
        encrypt_kwargs = {
            "plaintext": decrypted_bytes,
            "associated_data": self.field.qual_associated_data,
        }
        encrypt_mock.assert_called_once_with(**encrypt_kwargs)
        assert encrypted_bytes == encrypt_mock.side_effect(**encrypt_kwargs)

    def test_cache_name(self):
        """cache_name returns the correct cache attribute name."""

        # pylint: disable-next=unused-variable
        class Model(FakeEncryptedModel):
            field = self.field

            Meta = FakeModelMeta

        assert self.field.cache_name == "_field_decrypted_value"

    def _assert_pending_encryption(
        self,
        instance: EncryptedModel,
        field: BaseEncryptedField,
        value: t.Optional[str],
    ):
        pending_encryption = instance.__dict__[field.attname]
        assert isinstance(pending_encryption, _PendingEncryption)
        assert pending_encryption.value == value
        assert pending_encryption.instance == instance

    def test_set(self):
        """__set__ sets the field value correctly."""

        # Field must have a non-callable default for this test.
        assert self.field.default is not None and not callable(
            self.field.default
        )
        # Field2 must have a callable default for this test.
        assert self.field2.default is not None and callable(self.field2.default)

        class Model(FakeEncryptedModel):
            field = self.field
            field2 = self.field2

            Meta = FakeModelMeta

        instance = Model()

        # Initial value is the encrypted default.
        self._assert_pending_encryption(
            instance, self.field, self.field_default
        )
        self._assert_pending_encryption(
            instance, self.field2, self.field2_default
        )

        value = "initial_value"
        instance = Model(field=value)
        self._assert_pending_encryption(instance, self.field, value)

        # Set to None.
        instance.field = None
        assert instance.__dict__[self.field.attname] is None

        # Set to _TrustedCiphertext.
        trusted_ciphertext = _TrustedCiphertext(self.encrypted_default)
        instance.field = trusted_ciphertext
        assert (
            instance.__dict__[self.field.attname]
            == trusted_ciphertext.ciphertext
        )

        # Set to new value.
        value = "new_value"
        instance.field = value
        self._assert_pending_encryption(instance, self.field, value)

    # def test_value(self):
    #     """value returns a property that encrypts/decrypts the field's value."""
    #     field = BaseEncryptedField[str](
    #         associated_data="value", default=self.default
    #     )

    #     assert isinstance(field.value, property)
    #     assert field.value.fget is not None
    #     assert field.value.fset is not None
    #     assert field.value.fdel is None

    #     class ValidModel(EncryptedModel):
    #         associated_data = "model"

    #         _field = field
    #         value: str = field.value

    #         class Meta(TypedModelMeta):
    #             app_label = "codeforlife.user"

    #         dek_aead = FakeAead.as_mock()

    #     with patch.object(
    #         field, "bytes_to_value", return_value="value"
    #     ) as bytes_to_value_mock, patch.object(
    #         field, "value_to_bytes", return_value=b"bytes"
    #     ) as value_to_bytes_mock:
    #         instance = ValidModel()

    #         # Get the value.
    #         value = instance.value
    #         instance.dek_aead.decrypt.assert_called_once_with(
    #             ciphertext=self.default,
    #             associated_data=field.qual_associated_data,
    #         )
    #         bytes_to_value_mock.assert_called_once_with(self.decrypted_default)
    #         assert value == bytes_to_value_mock.return_value

    #         # Set the value.
    #         value = "new_value"
    #         instance.value = value
    #         value_to_bytes_mock.assert_called_once_with(value)
    #         instance.dek_aead.encrypt.assert_called_once_with(
    #             plaintext=value_to_bytes_mock.return_value,
    #             associated_data=field.qual_associated_data,
    #         )
    #         # pylint: disable-next=protected-access
    #         assert instance._field == FakeAead.encrypt(
    #             value_to_bytes_mock.return_value
    #         )
