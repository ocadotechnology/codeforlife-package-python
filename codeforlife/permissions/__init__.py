"""
© Ocado Group
Created on 14/12/2023 at 14:04:57(+00:00).
"""

import typing as t

from rest_framework.permissions import BasePermission

from .is_cron_request_from_google import IsCronRequestFromGoogle
from .is_self import IsSelf

AnyPermission = t.TypeVar("AnyPermission", bound=BasePermission)
