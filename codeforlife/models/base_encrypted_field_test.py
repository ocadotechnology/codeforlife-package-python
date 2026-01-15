import typing as t
from unittest.mock import MagicMock, patch

from django.db import models

from ..tests import TestCase
from .base_encrypted_field import BaseEncryptedField
from .encrypted import EncryptedModel

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


class EncryptedModelTestCase(TestCase):
    def setUp(self):
        self.associated_data = "field"
        self.default = b"default_encrypted_bytes"
        self.field = BaseEncryptedField[str](
            associated_data=self.associated_data, default=self.default
        )

    def test_init__no_associated_data(self):
        """Cannot create BaseEncryptedField with no associated data."""
        with self.assert_raises_validation_error(code="no_associated_data"):
            BaseEncryptedField(associated_data="")

    def test_init(self):
        """BaseEncryptedField is constructed correctly."""
        assert self.field.associated_data == self.associated_data
        assert self.field.db_column == self.associated_data

    def test_deconstruct(self):
        """BaseEncryptedField is deconstructed correctly."""
        _, _, _, kwargs = self.field.deconstruct()

        assert kwargs["associated_data"] == self.associated_data
        assert kwargs["db_column"] == self.associated_data

    def test_contribute_to_class__invalid_model_base_class(self):
        """Cannot contribute BaseEncryptedField to invalid model base class."""
        with self.assert_raises_validation_error(
            code="invalid_model_base_class"
        ):
            # pylint: disable-next=unused-variable,abstract-method
            class InvalidModel(models.Model):
                field = self.field

                class Meta(TypedModelMeta):
                    app_label = "codeforlife.user"

    def test_contribute_to_class__already_registered(self):
        """Cannot contribute BaseEncryptedField that is already registered."""
        with self.assert_raises_validation_error(code="already_registered"):
            # pylint: disable-next=unused-variable,abstract-method
            class InvalidModel(EncryptedModel):
                field = self.field
                field2 = self.field

                class Meta(TypedModelMeta):
                    app_label = "codeforlife.user"

    def test_contribute_to_class(self):
        """BaseEncryptedField is contributed to class correctly."""

        # pylint: disable-next=unused-variable,abstract-method
        class TestModel(EncryptedModel):
            associated_data = "model"

            field = self.field

            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

        assert self.field in TestModel.ENCRYPTED_FIELDS

    def test_contribute_to_class__associated_data_already_used(self):
        """
        Cannot contribute BaseEncryptedField with duplicate associated data.
        """
        with self.assert_raises_validation_error(
            code="associated_data_already_used"
        ):
            # pylint: disable-next=unused-variable,abstract-method
            class InvalidModel(EncryptedModel):
                field = self.field
                field2 = BaseEncryptedField(
                    associated_data=self.associated_data
                )

                class Meta(TypedModelMeta):
                    app_label = "codeforlife.user"

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

        # pylint: disable-next=abstract-method
        class ValidModel(EncryptedModel):
            associated_data = "model"

            field = self.field

            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

        assert (
            self.field.qual_associated_data
            == f"{ValidModel.associated_data}:{self.associated_data}".encode()
        )

    def test_value(self):
        """value returns a property that encrypts/decrypts the field's value."""
        field = BaseEncryptedField[str](
            associated_data="value", default=self.default
        )

        assert isinstance(field.value, property)
        assert field.value.fget is not None
        assert field.value.fset is not None
        assert field.value.fdel is None

        dek_aead_mock = MagicMock()
        dek_aead_decrypt_mock = MagicMock(return_value=b"decrypted_bytes")
        dek_aead_mock.decrypt = dek_aead_decrypt_mock
        dek_aead_encrypt_mock = MagicMock(return_value=b"encrypted_bytes")
        dek_aead_mock.encrypt = dek_aead_encrypt_mock

        class ValidModel(EncryptedModel):
            associated_data = "model"

            _field = field
            value: str = field.value

            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

            @property
            def dek_aead(self):
                return dek_aead_mock

        with patch.object(
            field, "bytes_to_value", return_value="value"
        ) as bytes_to_value_mock, patch.object(
            field, "value_to_bytes", return_value=b"bytes"
        ) as value_to_bytes_mock:
            instance = ValidModel()

            # Get the value.
            value = instance.value
            dek_aead_decrypt_mock.assert_called_once_with(
                ciphertext=self.default,
                associated_data=field.qual_associated_data,
            )
            bytes_to_value_mock.assert_called_once_with(
                dek_aead_decrypt_mock.return_value
            )
            assert value == bytes_to_value_mock.return_value

            # Set the value.
            value = "new_value"
            instance.value = value
            value_to_bytes_mock.assert_called_once_with(value)
            dek_aead_encrypt_mock.assert_called_once_with(
                plaintext=value_to_bytes_mock.return_value,
                associated_data=field.qual_associated_data,
            )
            # pylint: disable-next=protected-access
            assert instance._field == dek_aead_encrypt_mock.return_value

    def test_initialize(self):
        """BaseEncryptedField.initialize creates field and value property."""
        field, value = BaseEncryptedField.initialize(
            associated_data=self.associated_data
        )

        assert field.value == value
