"""
© Ocado Group
Created on 21/03/2025 at 17:43:17(+00:00).
"""

import re
import typing as t

import regex
from django.core.validators import RegexValidator, _ErrorMessage, _Regex
from django.utils.functional import SimpleLazyObject


def _lazy_re_compile(pattern, flags: int = 0):
    """Lazily compile a regex with flags."""

    def _compile():
        # Compile the regex if it was not passed pre-compiled.
        if isinstance(pattern, (str, bytes)):
            return regex.compile(pattern, flags)
        else:
            assert (
                not flags
            ), "flags must be empty if regex is passed pre-compiled"
            return pattern

    return SimpleLazyObject(_compile)


class EnhancedRegexValidator(RegexValidator):
    """Extends Django's default regex validator to support enhanced patterns."""

    def __init__(
        self,
        regex: t.Optional[_Regex] = None,
        message: t.Optional[_ErrorMessage] = None,
        code: t.Optional[str] = None,
        inverse_match: t.Optional[bool] = None,
        flags: t.Optional[re.RegexFlag] = None,
    ):
        super().__init__(
            regex=regex,
            message=message,
            code=code,
            inverse_match=inverse_match,
            flags=flags,
        )

        self.regex = _lazy_re_compile(self.regex, self.flags)
