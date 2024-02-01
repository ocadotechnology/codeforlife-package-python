"""
© Ocado Group
Created on 30/01/2024 at 17:41:00(+00:00).
"""

import typing as t

from ...models.user import User


# pylint: disable-next=too-few-public-methods
class PasswordValidator:
    """Base class for all password validators"""

    # pylint: disable-next=missing-function-docstring
    def validate(self, password: str, user: t.Optional[User] = None):
        raise NotImplementedError()
