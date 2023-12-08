"""
© Ocado Group
Created on 08/12/2023 at 17:43:11(+00:00).
"""

from ....tests import ModelTestCase
from ...models import School


class TestSchool(ModelTestCase[School]):
    """Tests the School model."""

    def test_constraints__no_uk_county_if_country_not_uk(self):
        """
        Cannot have set a UK county if the country is not set to UK.
        """

        raise NotImplementedError()  # TODO
