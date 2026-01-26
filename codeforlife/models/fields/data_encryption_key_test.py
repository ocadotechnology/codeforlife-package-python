"""
© Ocado Group
Created on 19/01/2026 at 09:57:10(+00:00).
"""

import typing as t

from django.db import models

from ...tests import TestCase
from .data_encryption_key import DataEncryptionKeyField, _Default

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


class DataEncryptionKeyFieldTestCase(TestCase):
    def _get_model_class(self):
        """Dynamically creates a Model subclass with a DEK field.

        This assigns self.field to the 'dek' attribute of the model.
        """

        class Model(models.Model):
            """A fake Model with a DEK field for testing."""

            dek = self.field

            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

        return Model

    def _get_model_instance(self, **kwargs):
        """Gets an instance of the dynamically created model class."""
        return self._get_model_class()(**kwargs)

    def setUp(self):
        # Casting as the field is not deferred in a model.
        self.field = t.cast(DataEncryptionKeyField, DataEncryptionKeyField())

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
        assert self.field.default == _Default
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
        assert kwargs["default"] == _Default
        assert kwargs["null"] is False
        assert (
            kwargs["verbose_name"]
            == DataEncryptionKeyField.default_verbose_name
        )
        assert kwargs["help_text"] == DataEncryptionKeyField.default_help_text

    def test_get__descriptor(self):
        """Getting field from class returns the descriptor."""
        Model = self._get_model_class()
        assert isinstance(Model.dek, DataEncryptionKeyField.descriptor_class)
        assert Model.dek.field == self.field

    def test_get__value(self):
        """Getting field from instance returns the DEK bytes."""
        instance = self._get_model_instance()
        dek_value = instance.dek
        assert isinstance(dek_value, bytes)
        assert dek_value == instance.__dict__["dek"]

    def test_set__default(self):
        """Setting field to _Default sets to default DEK bytes."""
        instance = self._get_model_instance()
        default = _Default()
        instance.dek = default
        assert default.dek == instance.__dict__["dek"]

    def test_set__none(self):
        """Setting field to None sets to None."""
        instance = self._get_model_instance()
        assert instance.dek is not None
        instance.dek = None
        assert instance.__dict__["dek"] is None

    def test_set__cannot_set_value(self):
        """Setting field to any value other than None or _Default raises."""
        instance = self._get_model_instance()
        with self.assert_raises_validation_error(code="cannot_set_value"):
            instance.dek = b"some_value"
