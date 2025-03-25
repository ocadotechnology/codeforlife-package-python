"""
© Ocado Group
Created on 21/03/2025 at 16:37:33(+00:00).

Unicode character set validators.
"""

import re
import typing as t

from .base import CharSetValidatorBuilder

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=duplicate-code


class UnicodeCharSetValidatorBuilder(CharSetValidatorBuilder):
    """Build a unicode character set with optional addons for reusability."""

    def __init__(
        self,
        char_set: str,
        description: str,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.UNICODE,
        spaces: bool = False,
        special_chars: str = "",
    ):
        if re.UNICODE not in flags:
            flags = flags | re.UNICODE

        super().__init__(
            char_set=char_set,
            description=description,
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class UnicodeAlphaCharSetValidator(UnicodeCharSetValidatorBuilder):
    """Validate all characters are within the unicode alpha set."""

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.UNICODE,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="\\p{L}",
            description="unicode alpha characters",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class LowercaseUnicodeAlphaCharSetValidator(UnicodeCharSetValidatorBuilder):
    """Validate all characters are within the lowercase unicode alpha set."""

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.UNICODE,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="\\p{Ll}",
            description="lowercase unicode alpha characters",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class UppercaseUnicodeAlphaCharSetValidator(UnicodeCharSetValidatorBuilder):
    """Validate all characters are within the uppercase unicode alpha set."""

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.UNICODE,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="\\p{Lu}",
            description="uppercase unicode alpha characters",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class UnicodeNumericCharSetValidator(UnicodeCharSetValidatorBuilder):
    """Validate all characters are within the unicode numeric set."""

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.UNICODE,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="\\p{N}",
            description="unicode numbers",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class UnicodeAlphanumericCharSetValidator(UnicodeCharSetValidatorBuilder):
    """Validate all characters are within the unicode alphanumeric set."""

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.UNICODE,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="\\p{L}\\p{N}",
            description="unicode alphanumeric characters",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class LowercaseUnicodeAlphanumericCharSetValidator(
    UnicodeCharSetValidatorBuilder
):
    """
    Validate all characters are within the lowercase unicode alphanumeric set.
    """

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.UNICODE,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="\\p{Ll}\\p{N}",
            description="lowercase unicode alphanumeric characters",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )


class UppercaseUnicodeAlphanumericCharSetValidator(
    UnicodeCharSetValidatorBuilder
):
    """
    Validate all characters are within the uppercase unicode alphanumeric set.
    """

    def __init__(
        self,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: re.RegexFlag = re.UNICODE,
        spaces: bool = False,
        special_chars: str = "",
    ):
        super().__init__(
            char_set="\\p{Lu}\\p{N}",
            description="uppercase unicode alphanumeric characters",
            code=code,
            inverse_match=inverse_match,
            flags=flags,
            spaces=spaces,
            special_chars=special_chars,
        )
