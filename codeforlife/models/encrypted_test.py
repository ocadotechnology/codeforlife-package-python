import typing as t

from ..tests import ModelTestCase
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
