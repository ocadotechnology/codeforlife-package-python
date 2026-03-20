"""
© Ocado Group
Created on 22/01/2026 at 13:43:46(+00:00).
"""

import typing as t

from django.db.models import Field, Model
from django.db.models.query_utils import DeferredAttribute as _DeferredAttribute

AnyModel = t.TypeVar("AnyModel", bound=Model)
AnyField = t.TypeVar("AnyField", bound=Field)
SetValue = t.TypeVar("SetValue")
InternalValue = t.TypeVar("InternalValue")
GetValue = t.TypeVar("GetValue")


# pylint: disable-next=too-few-public-methods
class DeferredAttribute(
    _DeferredAttribute,
    t.Generic[AnyModel, AnyField, SetValue, InternalValue, GetValue],
):
    """Custom DeferredAttribute with type hints ref to the field."""

    _field: AnyField

    @property
    def field(self):
        """Helper to get the field with the correct type."""
        # Mypy tries to be helpful here but fails to infer the correct type.
        # Hence the cast.
        return t.cast(AnyField, self._field)

    @field.setter
    def field(self, value: AnyField):
        self._field = value

    def from_internal_value(
        self,
        # pylint: disable=unused-argument
        instance: t.Optional[AnyModel],
        cls: t.Optional[t.Type[AnyModel]],
        # pylint: enable=unused-argument
        internal_value: InternalValue,
    ) -> t.Optional[GetValue]:
        """Convert the internal value to the value returned by __get__."""
        return t.cast(t.Optional[GetValue], internal_value)

    def __get__(
        self,
        instance: t.Optional[AnyModel],  # type: ignore[override]
        cls: t.Optional[t.Type[AnyModel]] = None,  # type: ignore[override]
    ):
        internal_value = t.cast(
            t.Union[t.Self, t.Optional[InternalValue]],
            super().__get__(instance, cls),  # type: ignore[misc]
        )

        # Return the descriptor itself when accessed on the class.
        if internal_value is self:
            return self

        # No value to process.
        if internal_value is None:
            return None

        return self.from_internal_value(
            instance, cls, t.cast(InternalValue, internal_value)
        )

    def to_internal_value(
        self,
        # pylint: disable-next=unused-argument
        instance: AnyModel,
        value: SetValue,
    ) -> t.Optional[InternalValue]:
        """Convert the value to the internal value stored by __set__."""
        return t.cast(t.Optional[InternalValue], value)

    def __set__(self, instance: AnyModel, value: t.Optional[SetValue]):
        # Set the internal value on the instance.
        internal_value = (
            None if value is None else self.to_internal_value(instance, value)
        )
        instance.__dict__[self.field.attname] = internal_value
