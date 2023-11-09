import typing as t

from . import AnyModel

UpdateFields = t.Optional[t.FrozenSet[str]]


def check_post_save(
    update_fields: UpdateFields,
    expected_update_fields: UpdateFields,
):
    """https://docs.djangoproject.com/en/3.2/ref/signals/#post-save

    Check if a model was updated with the expected fields.

    Args:
        update_fields: The fields that were updated.
        expected_update_fields: A subset of the fields that were expected to be
            updated. If no fields were expected to be updated, set to None.

    Returns:
        If the model instance was updated as expected.
    """

    if expected_update_fields is None:
        return update_fields is None
    elif update_fields is None:
        return False

    return all(
        update_field in update_fields for update_field in expected_update_fields
    )


def check_pre_save(
    update_fields: UpdateFields = None,
    expected_update_fields: UpdateFields = None,
    instance: t.Optional[AnyModel] = None,
    created: bool = False,
    created_only: bool = False,
):
    """https://docs.djangoproject.com/en/3.2/ref/signals/#pre-save

    Check if a model was created or updated with the expected fields.

    Args:
        update_fields: The fields that were updated.
        expected_update_fields: A subset of the fields that were expected to be
            updated. If no fields were expected to be updated, set to None.
        instance: Any model instance.
        created: Check if the model was created.
        created_only: Only check if the model was created.

    Raises:
        ValueError: If arg 'created' is True and arg 'instance' is None.

    Returns:
        If the model instance was created or updated as expected.
    """

    if created:
        if instance is None:
            raise ValueError("Arg 'instance' cannot be None.")
        if created_only:
            return instance.pk is None
        if instance.pk is None:
            return True

    return check_post_save(update_fields, expected_update_fields)
