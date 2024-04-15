"""
© Ocado Group
Created on 12/04/2024 at 15:07:35(+01:00).
"""

import typing as t
from unittest.case import _AssertRaisesContext

from django.db.models import Model
from django.db.utils import IntegrityError

from .test import TestCase

AnyModel = t.TypeVar("AnyModel", bound=Model)


class ModelTestCase(TestCase, t.Generic[AnyModel]):
    """Base for all model test cases."""

    @classmethod
    def get_model_class(cls) -> t.Type[AnyModel]:
        """Get the model's class.

        Returns:
            The model's class.
        """

        # pylint: disable-next=no-member
        return t.get_args(cls.__orig_bases__[0])[  # type: ignore[attr-defined]
            0
        ]

    def assert_raises_integrity_error(self, *args, **kwargs):
        """Assert the code block raises an integrity error.

        Returns:
            Error catcher that will assert if an integrity error is raised.
        """

        return self.assertRaises(IntegrityError, *args, **kwargs)

    def assert_check_constraint(self, name: str, *args, **kwargs):
        """Assert the code block raises a check-constraint error.

        Args:
            name: The name of the check constraint.

        Returns:
            An assertion context wrapper.
        """

        class Wrapper:
            """Wrap context to assert constraint name on exit."""

            def __init__(self, context: "_AssertRaisesContext[IntegrityError]"):
                self.context = context

            def __enter__(self, *args, **kwargs):
                return self.context.__enter__(*args, **kwargs)

            def __exit__(self, *args, **kwargs):
                value = self.context.__exit__(*args, **kwargs)
                assert (
                    self.context.exception.args[0]
                    == f"CHECK constraint failed: {name}"
                )
                return value

        return Wrapper(self.assert_raises_integrity_error(*args, **kwargs))

    def assert_does_not_exist(self, model_or_pk: t.Union[AnyModel, t.Any]):
        """Asserts the model does not exist.

        Args:
            model_or_pk: The model itself or its primary key.
        """

        model_class = self.get_model_class()
        with self.assertRaises(model_class.DoesNotExist):
            if isinstance(model_or_pk, Model):
                model_or_pk.refresh_from_db()
            else:
                model_class.objects.get(pk=model_or_pk)
