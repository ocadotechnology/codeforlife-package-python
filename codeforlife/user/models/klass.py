"""
© Ocado Group
Created on 19/02/2024 at 21:54:04(+00:00).
"""

# pylint: disable-next=unused-import
from common.models import Class  # type: ignore[import-untyped]
from django.core.validators import MaxLengthValidator, MinLengthValidator

from ...validators import (
    UnicodeAlphanumericCharSetValidator,
    UppercaseAsciiAlphanumericCharSetValidator,
)

class_access_code_validators = [
    MinLengthValidator(5),
    MaxLengthValidator(5),
    UppercaseAsciiAlphanumericCharSetValidator(),
]

class_name_validators = [
    UnicodeAlphanumericCharSetValidator(
        spaces=True,
        special_chars="-_",
    )
]
