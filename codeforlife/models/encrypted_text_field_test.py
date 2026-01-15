from ..tests import TestCase
from .encrypted_text_field import EncryptedTextField


# pylint: disable-next=missing-class-docstring
class EncryptedTextFieldTestCase(TestCase):
    def setUp(self):
        self.field = EncryptedTextField(associated_data="field")

    def test_bytes_to_value(self):
        """bytes_to_value decodes bytes to string."""
        data = b"hello world"
        value = self.field.bytes_to_value(data)
        assert value == data.decode()

    def test_value_to_bytes(self):
        """value_to_bytes encodes string to bytes."""
        value = "hello world"
        data = self.field.value_to_bytes(value)
        assert data == value.encode()
