"""
© Ocado Group
Created on 21/03/2025 at 16:23:06(+00:00).

ASCII character set validators.
"""

import re
import typing as t

from .base import CharSetValidatorBuilder

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=duplicate-code


class AsciiCharSetValidatorBuilder(CharSetValidatorBuilder):
    """Build an ASCII character set with optional addons for reusability."""

    def __init__(
        self,
        char_set: str,
        description: str,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.ASCII,
        spaces: bool = False,
        special_chars: str = "",
    ):
        if re.ASCII not in flags:
            flags = flags | re.ASCII

        super().__init__(
            char_set=char_set,
            description=description,
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class AsciiAlphaCharSetValidator(AsciiCharSetValidatorBuilder):
    """Validate all characters are within the ASCII alpha set (a-z, A-Z)."""

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.ASCII,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="a-zA-Z",
            description="ASCII alpha characters (a-z, A-Z)",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class LowercaseAsciiAlphaCharSetValidator(AsciiCharSetValidatorBuilder):
    """
    Validate all characters are within the lowercase ASCII alpha set (a-z).
    """

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.ASCII,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="a-z",
            description="lowercase ASCII alpha characters (a-z)",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class UppercaseAsciiAlphaCharSetValidator(AsciiCharSetValidatorBuilder):
    """
    Validate all characters are within the uppercase ASCII alpha set (A-Z).
    """

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.ASCII,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="A-Z",
            description="uppercase ASCII alpha characters (A-Z)",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class AsciiNumericCharSetValidator(AsciiCharSetValidatorBuilder):
    """Validate all characters are within the ASCII numeric set (0-9)."""

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.ASCII,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="0-9",
            description="ASCII numbers (0-9)",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class AsciiAlphanumericCharSetValidator(AsciiCharSetValidatorBuilder):
    """
    Validate all characters are within the ASCII alphanumeric set
    (a-z, A-Z, 0-9).
    """

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.ASCII,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="a-zA-Z0-9",
            description="ASCII alphanumeric characters (a-z, A-Z, 0-9)",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class LowercaseAsciiAlphanumericCharSetValidator(AsciiCharSetValidatorBuilder):
    """
    Validate all characters are within the lowercase ASCII alphanumeric set
    (a-z, 0-9).
    """

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.ASCII,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="a-z0-9",
            description="lowercase ASCII alphanumeric characters (a-z, 0-9)",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class UppercaseAsciiAlphanumericCharSetValidator(AsciiCharSetValidatorBuilder):
    """
    Validate all characters are within the uppercase ASCII alphanumeric set
    (A-Z, 0-9).
    """

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.ASCII,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="A-Z0-9",
            description="uppercase ASCII alphanumeric characters (A-Z, 0-9)",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )
