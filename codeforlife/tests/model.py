"""
© Ocado Group
Created on 08/12/2023 at 18:05:47(+00:00).

Test helpers for Django models.
"""

import typing as t

from django.db.models import Model
from django.db.utils import IntegrityError
from django.test import TestCase

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
