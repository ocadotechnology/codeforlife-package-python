"""
© Ocado Group
Created on 20/02/2024 at 15:37:52(+00:00).
"""

# pylint: disable-next=unused-import
from common.models import School  # type: ignore[import-untyped]

from ...types import Validators
from ...validators import UnicodeAlphanumericCharSetValidator

# TODO: add to School.name field-validators in new schema.
school_name_validators: Validators = [
    UnicodeAlphanumericCharSetValidator(
        spaces=True,
        special_chars="'.",
    )
]
