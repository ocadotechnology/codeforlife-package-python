"""Helpers for module "django.db.models.signals.pre_save".
https://docs.djangoproject.com/en/3.2/ref/signals/#pre-save
"""

import typing as t

from django.db.models import Model

from . import UpdateFields, _has_update_fields

AnyModel = t.TypeVar("AnyModel", bound=Model)


def was_created(instance: AnyModel):
    """Check if the instance was created.

    Args:
        instance: The current instance.

    Returns:
        If the instance was created.
    """

    return instance.pk is not None


def has_update_fields(actual: UpdateFields, expected: UpdateFields):
    """Check if the expected fields are going to be updated.

    Args:
        actual: The fields that are going to be updated.
        expected: A subset of the fields that are expected to be updated. If no
            fields are expected to be updated, set to None.

    Returns:
        If the fields that are expected to be updated are a subset of the
        fields that are going to be updated.
    """

    return _has_update_fields(actual, expected)


def check_previous_values(
    instance: AnyModel,
    predicates: t.Dict[str, t.Callable[[t.Any, t.Any], bool]],
):
    """Check if the previous values are as expected. If the model has not been
    created yet, the previous values are None.

    Args:
        instance: The current instance.
        predicates: A predicate for each field. It accepts the arguments
        (previous_value, value) and returns True if the values are as expected.

    Returns:
        If all the previous values are as expected.
    """

    if was_created(instance):
        previous_instance = instance.__class__.objects.get(pk=instance.pk)

        def get_previous_value(field: str):
            return getattr(previous_instance, field)

    else:
        # pylint: disable-next=unused-argument
        def get_previous_value(field: str):
            return None

    return all(
        predicate(get_previous_value(field), getattr(instance, field))
        for field, predicate in predicates.items()
    )


def previous_values_are_unequal(instance: AnyModel, fields: t.Set[str]):
    """Check if all the previous values are not equal to the current values. If
    the model has not been created yet, the previous values are None.

    Args:
        instance: The current instance.
        fields: The fields that should not be equal.

    Returns:
        If all the previous values are not equal to the current values.
    """

    def predicate(v1, v2):
        return v1 != v2

    return check_previous_values(
        instance,
        {field: predicate for field in fields},
    )
