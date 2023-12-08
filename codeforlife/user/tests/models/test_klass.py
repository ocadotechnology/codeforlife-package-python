"""
© Ocado Group
Created on 08/12/2023 at 17:43:11(+00:00).
"""

from ....tests import ModelTestCase
from ...models import Class


class TestClass(ModelTestCase[Class]):
    """Tests the Class model."""

    def test_id__validators__regex(self):
        """
        Check the regex validation of a class' ID.
        """

        raise NotImplementedError()  # TODO
