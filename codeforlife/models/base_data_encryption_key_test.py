"""
© Ocado Group
Created on 26/01/2026 at 13:44:31(+00:00).
"""

import typing as t
from unittest.mock import MagicMock, patch

from ..encryption import FakeAead
from ..tests import ModelTestCase
from .base_data_encryption_key import BaseDataEncryptionKeyModel
from .fields import DataEncryptionKeyField

if t.TYPE_CHECKING:
    from django_stubs_ext.db.models import TypedModelMeta
else:
    TypedModelMeta = object

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


class TestDataEncryptionKeyModel(ModelTestCase[BaseDataEncryptionKeyModel]):
    @classmethod
    def get_model_class(cls):
        """
        Dynamically create a subclass of BaseDataEncryptionKeyModel for testing.
        """

        class TestModel(BaseDataEncryptionKeyModel):
            dek: DataEncryptionKeyField = DataEncryptionKeyField()

            class Meta(TypedModelMeta):
                app_label = "codeforlife.user"

        return TestModel

    def get_model_instance(self, *args, **kwargs):
        return self.get_model_class()(*args, **kwargs)

    def test_dek_aead__none(self):
        """Returns None when dek is None."""
        instance = self.get_model_instance(dek=None)
        assert instance.dek_aead is None

    def test_dek_aead__unsaved_instance(self):
        """Cannot get dek before saving the instance."""
        instance = self.get_model_instance()
        with self.assert_raises_validation_error(code="unsaved_instance"):
            _ = instance.dek_aead

    @patch("codeforlife.models.base_data_encryption_key.get_dek_aead")
    def test_dek_aead__not_cached(self, get_dek_aead_mock: MagicMock):
        """Returns dek_aead and caches it when not cached."""
        # Create an instance with a primary key to mimic a saved instance.
        instance = self.get_model_instance(pk=1)
        assert instance.dek is not None

        # Setup the mock to return a FakeAead instance.
        dek_aead_mock = FakeAead.as_mock()
        get_dek_aead_mock.return_value = dek_aead_mock

        # Initially, the cache should not have the dek_aead. After accessing
        # dek_aead, it should be cached.
        assert instance.pk not in instance.DEK_AEAD_CACHE
        assert instance.dek_aead is dek_aead_mock
        assert instance.pk in instance.DEK_AEAD_CACHE

        # Ensure the get_dek_aead function was called with the correct dek.
        get_dek_aead_mock.assert_called_once_with(instance.dek)

    @patch("codeforlife.models.base_data_encryption_key.get_dek_aead")
    def test_dek_aead__cached(self, get_dek_aead_mock: MagicMock):
        """Returns the cached dek_aead."""
        # Create an instance with a primary key to mimic a saved instance.
        instance = self.get_model_instance(pk=1)
        assert instance.dek is not None

        # Pre-populate the cache with a FakeAead instance.
        dek_aead_mock = FakeAead.as_mock()
        instance.DEK_AEAD_CACHE[instance.pk] = dek_aead_mock

        # Accessing dek_aead should return the cached value.
        assert instance.dek_aead is dek_aead_mock

        # Ensure the get_dek_aead function was not called as its cached.
        get_dek_aead_mock.assert_not_called()
