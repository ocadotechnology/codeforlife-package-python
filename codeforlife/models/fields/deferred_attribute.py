"""
© Ocado Group
Created on 22/01/2026 at 13:43:46(+00:00).
"""

import typing as t

from django.db.models import Field, Model
from django.db.models.query_utils import DeferredAttribute as _DeferredAttribute

AnyModel = t.TypeVar("AnyModel", bound=Model)
AnyField = t.TypeVar("AnyField", bound=Field)


# pylint: disable-next=too-few-public-methods
class DeferredAttribute(_DeferredAttribute, t.Generic[AnyField, AnyModel]):
    """Custom DeferredAttribute with type hints ref to the field."""

    _field: AnyField

    @property
    def field(self):
        """Helper to get the field with the correct type."""
        return t.cast(AnyField, self._field)

    @field.setter
    def field(self, value: AnyField):
        self._field = value

    def __get__(self, instance: t.Optional[AnyModel], cls=None):
        # Return the descriptor itself when accessed on the class.
        if instance is None:
            return self

        # Get the internal value from the instance.
        return instance.__dict__.get(self.field.attname)

    def __set__(self, instance: AnyModel, value):
        # Set the internal value on the instance.
        instance.__dict__[self.field.attname] = value
