import typing as t

from ..tests import ModelTestCase
from ..user.models import OtpBypassToken
from .encrypted import EncryptedModel
from .encrypted_text_field import EncryptedTextField

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


# pylint: disable-next=abstract-method
class Person(EncryptedModel):
    associated_data = "person"

    _name, name = EncryptedTextField.initialize(associated_data="name")

    class Meta(TypedModelMeta):
        app_label = "codeforlife.user"


class EncryptedModelTestCase(ModelTestCase[EncryptedModel]):
    def test_init__cannot_set_encrypted_field(self):
        """Cannot set encrypted field via __init__."""
        with self.assert_raises_validation_error(
            code="cannot_set_encrypted_field"
        ):
            Person(_name="Alice")

    def test_objects___update__cannot_update_encrypted_field(self):
        """Cannot update encrypted field via objects.update()."""
        with self.assert_raises_validation_error(
            code="cannot_update_encrypted_field"
        ):
            Person.objects.update(_name="Alice")

    def test_dek_aead(self):
        """dek_aead raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            # pylint: disable-next=expression-not-assigned
            Person().dek_aead

    def test_check__e001(self):
        """Check for missing associated_data."""

        # pylint: disable-next=abstract-method
        class E001(EncryptedModel):
            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

        self.assert_check(
            error_id="codeforlife.user.E001",
            model_class=E001,
        )

    def test_check__e002(self):
        """Check for string associated_data."""

        # pylint: disable-next=abstract-method
        class E002(EncryptedModel):
            associated_data = 123  # type: ignore[assignment]

            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

        self.assert_check(
            error_id="codeforlife.user.E002",
            model_class=E002,
        )

    def test_check__e003(self):
        """Check for non-empty associated_data."""

        # pylint: disable-next=abstract-method
        class E003(EncryptedModel):
            associated_data = ""

            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

        self.assert_check(
            error_id="codeforlife.user.E003",
            model_class=E003,
        )

    def test_check__e004(self):
        """Check for unique associated_data."""

        # pylint: disable-next=abstract-method
        class E004(EncryptedModel):
            associated_data = OtpBypassToken.associated_data

            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

        self.assert_check(
            error_id="codeforlife.user.E004",
            model_class=E004,
        )
