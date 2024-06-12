"""
© Ocado Group
Created on 01/02/2024 at 14:44:16(+00:00).
"""

import typing as t

# isort: off
from common.helpers.generators import (  # type: ignore[import-untyped]
    get_hashed_login_id,
)

# isort: on

from ....request import HttpRequest
from ...models import Student, StudentUser
from .base import BaseBackend


class StudentAutoBackend(BaseBackend):
    """Authenticate a student using their ID and auto-generated password."""

    user_class = StudentUser

    def authenticate(  # type: ignore[override]
        self,
        request: t.Optional[HttpRequest],
        student_id: t.Optional[int] = None,
        auto_gen_password: t.Optional[str] = None,
        **kwargs
    ):
        if student_id is None or auto_gen_password is None:
            return None

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            student = None

        if student:
            # TODO: refactor this
            # Check the url against the student's stored hash.
            if (
                student.new_user
                and student.login_id
                and get_hashed_login_id(auto_gen_password) == student.login_id
            ):
                return student.new_user

        return None
