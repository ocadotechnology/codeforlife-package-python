"""
© Ocado Group
Created on 14/03/2024 at 13:08:13(+00:00).

Helpers for module "django.db.models.signals.pre_save".
https://docs.djangoproject.com/en/5.1/ref/signals/#pre-save
"""

import typing as t

from . import general as _

PREVIOUS_VALUE_KEY = "previous_{field}"


def adding(instance: _.AnyModel):
    """Check if the instance is being added to the database.

    Args:
        instance: The instance to check.

    Returns:
        A flag designating if the instance is being added to the database.
    """

    # pylint: disable-next=protected-access
    return instance._state.adding


def _generate_get_previous_value(
    instance: _.AnyModel,
) -> t.Callable[[str], t.Any]:
    if adding(instance):
        # pylint: disable-next=unused-argument
        def get_previous_value(field: str):
            return None

    else:
        objects = instance.__class__.objects  # type: ignore[attr-defined]
        previous_instance = objects.get(pk=instance.pk)

        def get_previous_value(field: str):
            return getattr(previous_instance, field)

    return get_previous_value


def check_previous_values(
    instance: _.AnyModel,
    predicates: t.Dict[str, t.Callable[[t.Any], bool]],
):
    # pylint: disable=line-too-long
    """Check if the previous values are as expected. If the model has not been
    created yet, the previous values are None.

    Args:
        instance: The current instance.
        predicates: A predicate for each field. The previous value is passed in as an arg and it should return True if the previous value is as expected.

    Returns:
        If all the previous values are as expected.
    """
    # pylint: enable=line-too-long

    get_previous_value = _generate_get_previous_value(instance)

    return all(
        predicate(get_previous_value(field))
        for field, predicate in predicates.items()
    )


def set_previous_values(instance: _.AnyModel, fields: t.Set[str]):
    # pylint: disable=line-too-long
    """Set the previous value of the specified fields. All fields are set on the
    instance with the naming convention: "previous_{field}".

    Args:
        instance: The current instance.
        fields: The fields to get the previous value for.
    """
    # pylint: enable=line-too-long

    get_previous_value = _generate_get_previous_value(instance)

    for field in fields:
        setattr(
            instance,
            PREVIOUS_VALUE_KEY.format(field=field),
            get_previous_value(field),
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

    get_previous_value = _generate_get_previous_value(instance)

    return all(
        get_previous_value(field) != getattr(instance, field)
        for field in fields
    )
