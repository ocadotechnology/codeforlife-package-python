"""
© Ocado Group
Created on 19/01/2026 at 09:57:10(+00:00).
"""

import typing as t

from django.db import models

from ...tests import TestCase
from ..base_data_encryption_key import BaseDataEncryptionKeyModel
from .data_encryption_key import DataEncryptionKeyField, _Default

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


class FakeModelMeta(TypedModelMeta):
    """A fake Meta class for testing."""

    app_label = "codeforlife.user"


class TestDataEncryptionKeyField(TestCase):
    # --------------------------------------------------------------------------
    # Test Helper Methods
    # --------------------------------------------------------------------------

    def _get_model_class(self):
        """Dynamically creates a Model subclass with a DEK field.

        This assigns self.field to the 'dek' attribute of the model.
        """

        class DekModel(BaseDataEncryptionKeyModel):
            """A fake Model with a DEK field for testing."""

            dek = self.field

            Meta = FakeModelMeta

        return DekModel

    def _get_model_instance(self, **kwargs):
        """Gets an instance of the dynamically created model class."""
        return self._get_model_class()(**kwargs)

    def setUp(self):
        # Casting as the field is not deferred in a model.
        self.field = t.cast(DataEncryptionKeyField, DataEncryptionKeyField())
        self.field2 = t.cast(DataEncryptionKeyField, DataEncryptionKeyField())

    # --------------------------------------------------------------------------
    # Construction & Deconstruction Tests
    # --------------------------------------------------------------------------

    def test_init__editable_not_allowed(self):
        """Cannot create DataEncryptionKeyField with editable=True."""
        with self.assert_raises_validation_error(code="editable_not_allowed"):
            DataEncryptionKeyField(editable=True)

    def test_init__default_not_allowed(self):
        """Cannot create DataEncryptionKeyField with default value."""
        with self.assert_raises_validation_error(code="default_not_allowed"):
            DataEncryptionKeyField(default=b"default_value")

    def test_init__null_allowed(self):
        """Cannot create DataEncryptionKeyField with null=True."""
        with self.assert_raises_validation_error(code="null_not_allowed"):
            DataEncryptionKeyField(null=False)

    def test_init(self):
        """DataEncryptionKeyField is constructed correctly."""
        assert self.field.editable is False
        assert self.field.default == _Default
        assert self.field.null is True
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
        assert kwargs["null"] is True
        assert (
            kwargs["verbose_name"]
            == DataEncryptionKeyField.default_verbose_name
        )
        assert kwargs["help_text"] == DataEncryptionKeyField.default_help_text

    # --------------------------------------------------------------------------
    # Django Model Field Integration Tests
    # --------------------------------------------------------------------------

    def test_contribute_to_class__invalid_model_base_class(self):
        """
        Cannot contribute DataEncryptionKeyField to invalid model base class.
        """
        with self.assert_raises_validation_error(
            code="invalid_model_base_class"
        ):
            # pylint: disable-next=unused-variable
            class Model(models.Model):
                field = self.field

                Meta = FakeModelMeta

    def test_contribute_to_class__multiple_dek_fields_not_allowed(self):
        """
        Cannot contribute multiple DataEncryptionKeyFields to a model.
        """
        with self.assert_raises_validation_error(
            code="multiple_dek_fields_not_allowed"
        ):
            # pylint: disable-next=unused-variable
            class Model(BaseDataEncryptionKeyModel):
                dek1 = self.field
                dek2 = self.field2

                Meta = FakeModelMeta

    def test_contribute_to_class(self):
        """DataEncryptionKeyField is contributed to model correctly."""
        with self.subTest("Class attribute set correctly"):
            Model = self._get_model_class()
            # pylint: disable-next=protected-access
            assert Model._dek == Model.dek

        with self.subTest("Instance attribute set correctly"):
            instance = Model()
            # pylint: disable-next=protected-access
            assert instance._dek == instance.dek

    # --------------------------------------------------------------------------
    # Descriptor Methods Tests
    # --------------------------------------------------------------------------

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
