"""
© Ocado Group
Created on 14/03/2024 at 13:08:13(+00:00).

Helpers for module "django.db.models.signals.pre_save".
https://docs.djangoproject.com/en/3.2/ref/signals/#pre-save
"""

import typing as t

from . import general as _


def adding(instance: _.AnyModel):
    """Check if the instance is being added to the database.

    Args:
        instance: The instance to check.

    Returns:
        A flag designating if the instance is being added to the database.
    """

    # pylint: disable-next=protected-access
    return instance._state.adding


def check_previous_values(
    instance: _.AnyModel,
    predicates: t.Dict[str, t.Callable[[t.Any, t.Any], bool]],
):
    # pylint: disable=line-too-long
    """Check if the previous values are as expected. If the model has not been
    created yet, the previous values are None.

    Args:
        instance: The current instance.
        predicates: A predicate for each field. It accepts the arguments (previous_value, value) and returns True if the values are as expected.

    Returns:
        If all the previous values are as expected.
    """
    # pylint: enable=line-too-long

    if adding(instance):
        # pylint: disable-next=unused-argument
        def get_previous_value(field: str):
            return None

    else:
        previous_instance = instance.__class__.objects.get(pk=instance.pk)

        def get_previous_value(field: str):
            return getattr(previous_instance, field)

    return all(
        predicate(get_previous_value(field), getattr(instance, field))
        for field, predicate in predicates.items()
    )


def previous_values_are_unequal(instance: _.AnyModel, fields: t.Set[str]):
    # pylint: disable=line-too-long
    """Check if all the previous values are not equal to the current values. If
    the model has not been created yet, the previous values are None.

    Args:
        instance: The current instance.
        fields: The fields that should not be equal.

    Returns:
        If all the previous values are not equal to the current values.
    """
    # pylint: enable=line-too-long

    def predicate(v1, v2):
        return v1 != v2

    return check_previous_values(
        instance, {field: predicate for field in fields}
    )
