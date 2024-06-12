"""
© Ocado Group
Created on 01/02/2024 at 14:48:57(+00:00).
"""

# TODO: Create a custom auth backend for Django admin permissions
from .email import EmailBackend
from .otp import OtpBackend
from .otp_bypass_token import OtpBypassTokenBackend
from .student import StudentBackend
from .student_auto import StudentAutoBackend
