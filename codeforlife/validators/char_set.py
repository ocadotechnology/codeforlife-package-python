"""
© Ocado Group
Created on 14/03/2025 at 08:35:04(+00:00).

Validators the limit the character set of text/char field.
"""

import re

from django.core.validators import RegexValidator

# pylint: disable=too-few-public-methods


class CharSetValidator(RegexValidator):
    """Validates all characters are within the allowed set."""

    def __init__(self, char_set: str, message: str):
        super().__init__(rf"^[{char_set}]*$", message)


class CharSetValidatorBuilder(CharSetValidator):
    """Build a character set with optional addons for reusability."""

    def __init__(
        self,
        char_set: str,
        description: str,
        spaces: bool = False,
        special_chars: str = "",
    ):
        message = f"can only contain: ${description}"

        if spaces:
            char_set += " "
            message += ", spaces"
        if special_chars:
            char_set += re.escape(special_chars)
            message += f", special characters ({special_chars})"

        super().__init__(char_set, message)


class AlphaCharSetValidator(CharSetValidatorBuilder):
    """Validate all characters are within the alpha set (a-z, A-Z)."""

    def __init__(self, spaces: bool = False, special_chars: str = ""):
        super().__init__(
            "a-zA-Z",
            "alpha characters (a-z, A-Z)",
            spaces,
            special_chars,
        )


class NumericCharSetValidator(CharSetValidatorBuilder):
    """Validate all characters are within the numeric set (0-9)."""

    def __init__(self, spaces: bool = False, special_chars: str = ""):
        super().__init__(
            "0-9",
            "numbers (0-9)",
            spaces,
            special_chars,
        )


class AlphanumericCharSetValidator(CharSetValidatorBuilder):
    """
    Validate all characters are within the alphanumeric set (a-z, A-Z, 0-9).
    """

    def __init__(self, spaces: bool = False, special_chars: str = ""):
        super().__init__(
            "a-zA-Z0-9",
            "alphanumeric characters (a-z, A-Z, 0-9)",
            spaces,
            special_chars,
        )


class LowercaseAlphaCharSetValidator(CharSetValidatorBuilder):
    """Validate all characters are within the lowercase alpha set (a-z)."""

    def __init__(self, spaces: bool = False, special_chars: str = ""):
        super().__init__(
            "a-z",
            "lowercase alpha characters (a-z)",
            spaces,
            special_chars,
        )


class LowercaseAlphanumericCharSetValidator(CharSetValidatorBuilder):
    """
    Validate all characters are within the lowercase alphanumeric set
    (a-z, 0-9).
    """

    def __init__(self, spaces: bool = False, special_chars: str = ""):
        super().__init__(
            "a-z0-9",
            "lowercase alphanumeric characters (a-z, 0-9)",
            spaces,
            special_chars,
        )


class UppercaseAlphaCharSetValidator(CharSetValidatorBuilder):
    """Validate all characters are within the uppercase alpha set (A-Z)."""

    def __init__(self, spaces: bool = False, special_chars: str = ""):
        super().__init__(
            "A-Z",
            "uppercase alpha characters (A-Z)",
            spaces,
            special_chars,
        )


class UppercaseAlphanumericCharSetValidator(CharSetValidatorBuilder):
    """
    Validate all characters are within the uppercase alphanumeric set
    (A-Z, 0-9).
    """

    def __init__(self, spaces: bool = False, special_chars: str = ""):
        super().__init__(
            "A-Z0-9",
            "uppercase alphanumeric characters (A-Z, 0-9)",
            spaces,
            special_chars,
        )
