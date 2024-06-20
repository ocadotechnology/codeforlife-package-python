"""
© Ocado Group
Created on 20/06/2024 at 11:46:02(+01:00).

Helpers for module "django.db.models.signals.post_save".
https://docs.djangoproject.com/en/3.2/ref/signals/#post-save
"""

import typing as t

from . import general as _
from .pre_save import PREVIOUS_VALUE_KEY

FieldValue = t.TypeVar("FieldValue")


def has_previous_values(instance: _.AnyModel, fields: t.Dict[str, t.Type]):
    # pylint: disable=line-too-long
    """Check if the instance has the specified previous values and that the
    values are an instance of the specified type.

    Args:
        instance: The current instance.
        fields: The fields the instance should have and the type of each value.

    Returns:
        If the instance has all the previous values and all the values are of
        the expected type.
    """
    # pylint: enable=line-too-long

    for field, cls in fields.items():
        previous_value_key = PREVIOUS_VALUE_KEY.format(field=field)

        if not hasattr(instance, previous_value_key) or not isinstance(
            getattr(instance, previous_value_key), cls
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
