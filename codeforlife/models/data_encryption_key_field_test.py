import typing as t
from unittest.mock import MagicMock, patch

from django.db import models

from ..encryption import create_dek
from ..tests import TestCase
from .data_encryption_key_field import DataEncryptionKeyField

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


class DataEncryptionKeyFieldTestCase(TestCase):
    def setUp(self):
        self.field: DataEncryptionKeyField = DataEncryptionKeyField()

    def test_init__editable_not_allowed(self):
        """Cannot create DataEncryptionKeyField with editable=True."""
        with self.assert_raises_validation_error(code="editable_not_allowed"):
            DataEncryptionKeyField(editable=True)

    def test_init__default_not_allowed(self):
        """Cannot create DataEncryptionKeyField with default value."""
        with self.assert_raises_validation_error(code="default_not_allowed"):
            DataEncryptionKeyField(default=b"default_value")

    def test_init__null_not_allowed(self):
        """Cannot create DataEncryptionKeyField with null=True."""
        with self.assert_raises_validation_error(code="null_not_allowed"):
            DataEncryptionKeyField(null=True)

    def test_init(self):
        """DataEncryptionKeyField is constructed correctly."""
        assert self.field.editable is False
        # pylint: disable-next=comparison-with-callable
        assert self.field.default == create_dek
        assert self.field.null is False
        assert (
            self.field.verbose_name
            == DataEncryptionKeyField.default_verbose_name
        )
        assert self.field.help_text == DataEncryptionKeyField.default_help_text

    def test_deconstruct(self):
        """DataEncryptionKeyField is deconstructed correctly."""
        _, _, _, kwargs = self.field.deconstruct()

        assert kwargs["editable"] is False
        # pylint: disable-next=comparison-with-callable
        assert kwargs["default"] == create_dek
        assert kwargs["null"] is False
        assert (
            kwargs["verbose_name"]
            == DataEncryptionKeyField.default_verbose_name
        )
        assert kwargs["help_text"] == DataEncryptionKeyField.default_help_text

    @patch(
        "codeforlife.models.data_encryption_key_field.create_dek",
        return_value=b"mock_dek_bytes",
    )
    @patch(
        "codeforlife.models.data_encryption_key_field.get_dek_aead",
        return_value="mock_dek_aead",
    )
    def test_aead(
        self, mock_get_dek_aead: MagicMock, mock_create_dek: MagicMock
    ):
        """AEAD returns a property that gets the AEAD for the DEK."""

        class ValidModel(models.Model):
            associated_data = "model"

            _dek: DataEncryptionKeyField = DataEncryptionKeyField()
            dek_aead = _dek.aead

            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

        instance = ValidModel()
        mock_create_dek.assert_called_once_with()

        mock_get_dek_aead.assert_not_called()
        dek_aead = instance.dek_aead
        mock_get_dek_aead.assert_called_once_with(mock_create_dek.return_value)
        assert dek_aead == mock_get_dek_aead.return_value

    def test_initialize(self):
        """DataEncryptionKeyField.initialize creates field and aead property."""
        field, aead = DataEncryptionKeyField.initialize()

        assert field.aead == aead
