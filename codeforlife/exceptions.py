"""
© Ocado Group
Created on 06/10/2025 at 10:45:41(+01:00).
"""


class Error(Exception):
    """Base class for all custom errors."""

    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.code = code


class ValidationError(Error):
    """Raised when a validation fails."""
