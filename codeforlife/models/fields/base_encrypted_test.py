"""
© Ocado Group
Created on 19/01/2026 at 09:56:57(+00:00).
"""

import typing as t
from functools import cached_property
from unittest.mock import MagicMock

from django.db import models

from ...encryption import FakeAead
from ...tests import InterruptPipelineError, TestCase
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

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes


class FakeEncryptedModel(EncryptedModel):
    """A fake EncryptedModel without fields for testing."""

    associated_data = "model"

    class Meta(TypedModelMeta):
        abstract = True

    @cached_property
    def dek_aead(self):
        return FakeAead.as_mock()

    def get_stored_value(self, field: BaseEncryptedField):
        """Gets the stored value for the given field."""
        assert field in self.ENCRYPTED_FIELDS
        return self.__dict__[field.attname]

    def set_stored_value(self, field: BaseEncryptedField, value):
        """Sets the stored value for the given field."""
        assert field in self.ENCRYPTED_FIELDS
        self.__dict__[field.attname] = value

    def assert_value_is_pending_encryption(
        self, field: BaseEncryptedField, value: str
    ):
        """
        Asserts the value for the given field is pending encryption.
        """
        pending_encryption = self.get_stored_value(field)
        assert isinstance(pending_encryption, _PendingEncryption)
        assert pending_encryption.value == value


class FakeModelMeta(TypedModelMeta):
    """A fake Meta class for testing."""

    app_label = "codeforlife.user"


# pylint: disable-next=abstract-method
class FakeEncryptedField(BaseEncryptedField[str]):
    """A fake BaseEncryptedField for testing."""

    value_to_bytes: MagicMock
    bytes_to_value: MagicMock
    encrypt_value: MagicMock
    decrypt_value: MagicMock

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
        self.encrypt_value = MagicMock(side_effect=super().encrypt_value)
        self.decrypt_value = MagicMock(side_effect=super().decrypt_value)


# pylint: disable-next=too-many-public-methods
class TestEncryptedModel(TestCase):
    """Tests BaseEncryptedField functionality."""

    # --------------------------------------------------------------------------
    # Test Helper Methods
    # --------------------------------------------------------------------------

    def _get_model_class(self):
        """Dynamically creates a FakeEncryptedModel subclass with fields.

        This assigns self.field and self.field2 to the model.
        """

        class Model(FakeEncryptedModel):
            """A fake EncryptedModel with fields for testing."""

            field = self.field
            field2 = self.field2

            Meta = FakeModelMeta

        return Model

    def _get_model_instance(self, **kwargs):
        """Gets an instance of the dynamically created model class."""
        return self._get_model_class()(**kwargs)

    def setUp(self):
        # Set up the first field with a non-callable default for testing.
        self.field_associated_data = "field"
        self.field_default = "default"
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

    # --------------------------------------------------------------------------
    # Construction & Deconstruction Tests
    # --------------------------------------------------------------------------

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

    # --------------------------------------------------------------------------
    # Django Model Field Integration Tests
    # --------------------------------------------------------------------------

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
        Model = self._get_model_class()  # Assign fields to model.
        self.assertListEqual(Model.ENCRYPTED_FIELDS, [self.field, self.field2])

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

    # --------------------------------------------------------------------------
    # Encryption & Decryption Tests
    # --------------------------------------------------------------------------

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
        Model = self._get_model_class()
        assert (
            self.field.qual_associated_data
            == f"{Model.associated_data}:{self.field_associated_data}".encode()
        )

    def test_decrypt_value(self):
        """decrypt_value decrypts the given ciphertext."""
        # Create instance and mock shorthands.
        instance = self._get_model_instance()
        decrypt_mock: MagicMock = instance.dek_aead.decrypt
        bytes_to_value_mock: MagicMock = self.field.bytes_to_value

        # When ciphertext is None, no decryption occurs.
        decrypted_value = self.field.decrypt_value(instance, ciphertext=None)
        assert decrypted_value is None
        decrypt_mock.assert_not_called()
        bytes_to_value_mock.assert_not_called()

        # When ciphertext is provided, decryption occurs.
        ciphertext = FakeAead.encrypt(b"value")
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
        # Create instance and mock shorthands.
        instance = self._get_model_instance()
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

    # --------------------------------------------------------------------------
    # Getting & Setting Values Tests
    # --------------------------------------------------------------------------

    def test_cache_name(self):
        """cache_name returns the correct cache attribute name."""
        self._get_model_class()  # Assign field to model.
        assert self.field.cache_name == "_field_decrypted_value"

    def test_set__default(self):
        """Setting field to default value stores pending encryption."""
        # Field must have a non-callable default for this test.
        assert self.field.default is not None and not callable(
            self.field.default
        )
        # Field2 must have a callable default for this test.
        assert self.field2.default is not None and callable(self.field2.default)

        instance = self._get_model_instance()
        instance.assert_value_is_pending_encryption(
            self.field, self.field_default
        )
        instance.assert_value_is_pending_encryption(
            self.field2, self.field2_default
        )

    def test_set__init(self):
        """Setting field to initial value stores pending encryption."""
        value = "initial_value"
        instance = self._get_model_instance(field=value)
        instance.assert_value_is_pending_encryption(self.field, value)

    def test_set__none(self):
        """Setting field to None stores None."""
        assert self.field.default is not None
        instance = self._get_model_instance(field=None)
        assert instance.get_stored_value(self.field) is None

    def test_set__trusted_ciphertext(self):
        """Setting field to _TrustedCiphertext stores ciphertext directly."""
        ciphertext = b"encrypted_value"
        trusted_ciphertext = _TrustedCiphertext(ciphertext)
        instance = self._get_model_instance(field=trusted_ciphertext)
        assert instance.get_stored_value(self.field) == ciphertext

    def test_set__new_value(self):
        """
        Setting field to new value stores pending encryption and clears cache.
        """
        assert self.field.default is not None

        value = "new_value"
        assert self.field.default != value

        instance = self._get_model_instance()

        # Cache the value on the instance.
        setattr(instance, self.field.cache_name, value)

        # Clear cache by setting to new value.
        instance.field = value
        instance.assert_value_is_pending_encryption(self.field, value)

        # Ensure cached value is cleared.
        assert not hasattr(instance, self.field.cache_name)

    def test_get__descriptor(self):
        """Getting field from class returns the descriptor."""
        Model = self._get_model_class()
        assert isinstance(Model.field, BaseEncryptedField.descriptor_class)
        assert Model.field.field == self.field

    def test_get__cached(self):
        """Getting field when cached returns cached value."""
        value = "decrypted_value"
        assert value != self.field.default

        instance = self._get_model_instance()
        setattr(instance, self.field.cache_name, value)
        assert instance.field == value

    def test_get__none(self):
        """Getting field when stored value is None returns None."""
        instance = self._get_model_instance()
        instance.set_stored_value(self.field, None)

        assert instance.field is None
        self.field.decrypt_value.assert_not_called()

    def test_get__pending_encryption(self):
        """
        Getting field when stored value is pending encryption returns value.
        """
        instance = self._get_model_instance()
        value = "decrypted_value"
        pending_encryption = _PendingEncryption(value)
        instance.set_stored_value(self.field, pending_encryption)

        assert instance.field == value
        self.field.decrypt_value.assert_not_called()

    def test_get__decrypted_value(self):
        """Getting field when stored value is ciphertext returns decrypted."""
        plaintext = "decrypted_value"
        ciphertext = FakeAead.encrypt(plaintext.encode())

        # Create instance with stored ciphertext.
        instance = self._get_model_instance()
        instance.set_stored_value(self.field, ciphertext)

        # Ensure cache is not set initially.
        assert not hasattr(instance, self.field.cache_name)

        # Get the field value, which should decrypt the ciphertext.
        assert instance.field == plaintext
        self.field.decrypt_value.assert_called_once_with(instance, ciphertext)

        # Ensure decrypted value is cached on the instance.
        assert getattr(instance, self.field.cache_name) == plaintext

    # --------------------------------------------------------------------------
    # pre_save Tests
    # --------------------------------------------------------------------------

    def test_pre_save__pending_encryption(self):
        """pre_save encrypts pending encryption before saving."""
        # Create instance with pending encryption.
        instance = self._get_model_instance()
        pending_encryption = instance.get_stored_value(self.field)
        assert isinstance(pending_encryption, _PendingEncryption)

        # Assert the value is encrypted in pre_save.
        def assert_pre_save(result):
            self.field.encrypt_value.assert_called_once_with(
                instance, pending_encryption.value
            )
            assert result == self.field.encrypt_value.side_effect(
                instance, pending_encryption.value
            )

        # Run the save pipeline, interrupting at pre_save.
        InterruptPipelineError.run(
            test_case=self,
            step_target=self.field,
            step_attribute="pre_save",
            assert_step=assert_pre_save,
            pipeline=instance.save,
        )

    def test_pre_save__none(self):
        """pre_save with no value does nothing."""
        # Create instance with no stored value.
        instance = self._get_model_instance()
        instance.set_stored_value(self.field, None)

        # Assert pre_save does nothing.
        def assert_pre_save(result):
            assert result is None
            self.field.encrypt_value.assert_not_called()

        # Run the save pipeline, interrupting at pre_save.
        InterruptPipelineError.run(
            test_case=self,
            step_target=self.field,
            step_attribute="pre_save",
            assert_step=assert_pre_save,
            pipeline=instance.save,
        )

    def test_pre_save__trusted_ciphertext(self):
        """pre_save with trusted ciphertext does nothing."""
        # Create instance with trusted ciphertext.
        ciphertext = b"encrypted_value"
        trusted_ciphertext = _TrustedCiphertext(ciphertext)
        instance = self._get_model_instance(field=trusted_ciphertext)

        # Assert pre_save returns the ciphertext directly.
        def assert_pre_save(result):
            assert result == ciphertext
            self.field.encrypt_value.assert_not_called()

        # Run the save pipeline, interrupting at pre_save.
        InterruptPipelineError.run(
            test_case=self,
            step_target=self.field,
            step_attribute="pre_save",
            assert_step=assert_pre_save,
            pipeline=instance.save,
        )

    def test_pre_save__invalid_value_type(self):
        """pre_save with invalid value type raises ValidationError."""
        # Create instance with invalid stored value.
        instance = self._get_model_instance()
        instance.set_stored_value(self.field, 12345)  # Invalid type.

        # Run the save pipeline, interrupting at pre_save.
        with self.assert_raises_validation_error(code="invalid_value_type"):
            instance.save()
