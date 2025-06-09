"""
© Ocado Group
Created on 20/06/2024 at 11:46:02(+01:00).

Helpers for module "django.db.models.signals.post_save".
https://docs.djangoproject.com/en/5.1/ref/signals/#post-save
"""

import typing as t

from . import general as _
from .pre_save import PREVIOUS_VALUE_KEY

FieldValue = t.TypeVar("FieldValue")


def check_previous_values(
    instance: _.AnyModel,
    predicates: t.Dict[str, t.Callable[[t.Any], bool]],
):
    # pylint: disable=line-too-long
    """Check if the previous values are as expected. If the previous value's key
    is not on the model, this check returns False.

    Args:
        instance: The current instance.
        predicates: A predicate for each field. The previous value is passed in as an arg and it should return True if the previous value is as expected.

    Returns:
        If all the previous values are as expected.
    """
    # pylint: enable=line-too-long

    for field, predicate in predicates.items():
        previous_value_key = PREVIOUS_VALUE_KEY.format(field=field)

        if not hasattr(instance, previous_value_key) or not predicate(
            getattr(instance, previous_value_key)
        ):
            return False

    return True


def previous_values_are_unequal(instance: _.AnyModel, fields: t.Set[str]):
    # pylint: disable=line-too-long
    """Check if all the previous values are not equal to the current values. If
    the previous value's key is not on the model, this check returns False.

    Args:
        instance: The current instance.
        fields: The fields that should not be equal.

    Returns:
        If all the previous values are not equal to the current values.
    """
    # pylint: enable=line-too-long

    for field in fields:
        previous_value_key = PREVIOUS_VALUE_KEY.format(field=field)

        if not hasattr(instance, previous_value_key) or (
            getattr(instance, field) == getattr(instance, previous_value_key)
        ):
            return False

    return True


def get_previous_value(
    instance: _.AnyModel, field: str, cls: t.Type[FieldValue]
):
    # pylint: disable=line-too-long
    """Get a previous value from the instance and assert the value is of the
    expected type.

    Args:
        instance: The current instance.
        field: The field to get the previous value for.
        cls: The expected type of the value.

    Returns:
        The previous value of the field.
    """
    # pylint: enable=line-too-long

    previous_value = getattr(instance, PREVIOUS_VALUE_KEY.format(field=field))

    assert isinstance(previous_value, cls)

    return previous_value
