"""
© Ocado Group
Created on 22/01/2026 at 13:43:46(+00:00).
"""

import typing as t

from django.db.models import Field
from django.db.models.query_utils import DeferredAttribute as _DeferredAttribute

AnyField = t.TypeVar("AnyField", bound=Field)


# pylint: disable-next=too-few-public-methods
class DeferredAttribute(_DeferredAttribute, t.Generic[AnyField]):
    """Custom DeferredAttribute with type hints ref to the field."""

    _field: AnyField

    @property
    def field(self):
        """Helper to get the field with the correct type."""
        return t.cast(AnyField, self._field)

    @field.setter
    def field(self, value: AnyField):
        self._field = value
