"""
© Ocado Group
Created on 16/04/2024 at 14:54:18(+01:00).
"""

from ...tests import ModelTestCase
from .student import Independent


# pylint: disable-next=missing-class-docstring
class TestIndependent(ModelTestCase[Independent]):
    def test_objects__get_queryset(self):
        """Check if only get independent students."""
        self.assert_get_queryset(
            # pylint: disable-next=line-too-long
            values=Independent.objects.filter(class_field__isnull=True)  # type: ignore[arg-type]
        )
