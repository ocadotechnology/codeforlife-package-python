"""
© Ocado Group
Created on 08/12/2023 at 18:05:47(+00:00).

Test helpers for Django models.
"""

import typing as t

from django.db.utils import IntegrityError
from django.test import TestCase

from ..models import AnyModel, Model


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

    def assert_does_not_exist(self, model_or_pk: t.Union[AnyModel, t.Any]):
        """Asserts the model does not exist.

        Args:
            model_or_pk: The model itself or its primary key.
        """

        if isinstance(model_or_pk, Model):
            with self.assertRaises(model_or_pk.DoesNotExist):
                model_or_pk.refresh_from_db()
        else:
            model_class = self.get_model_class()
            with self.assertRaises(model_class.DoesNotExist):
                model_class.objects.get(pk=model_or_pk)
