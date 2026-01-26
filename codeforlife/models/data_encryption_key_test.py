"""
© Ocado Group
Created on 26/01/2026 at 13:44:31(+00:00).
"""

import typing as t
from unittest.mock import MagicMock, patch

from ..encryption import FakeAead
from ..tests import ModelTestCase
from .data_encryption_key import DataEncryptionKeyModel

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


class TestDataEncryptionKeyModel(ModelTestCase[DataEncryptionKeyModel]):
    @classmethod
    def get_model_class(cls):
        """
        Dynamically create a subclass of DataEncryptionKeyModel for testing.
        """

        class TestModel(DataEncryptionKeyModel):
            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

        return TestModel

    @patch("codeforlife.models.data_encryption_key.get_dek_aead")
    def test_dek_aead(self, get_dek_aead_mock: MagicMock):
        """dek_aead property returns None when dek is not set."""
        instance = self.get_model_instance()

        with self.subTest("When dek is set"):
            dek_aead_mock = FakeAead.as_mock()
            get_dek_aead_mock.return_value = dek_aead_mock
            assert instance.dek_aead is dek_aead_mock
            get_dek_aead_mock.assert_called_once_with(instance.dek)

        with self.subTest("When dek is None"):
            get_dek_aead_mock.reset_mock()
            instance.dek = None
            assert instance.dek_aead is None
