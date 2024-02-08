"""
© Ocado Group
Created on 05/02/2024 at 13:48:55(+00:00).
"""

# from .other import *
# from .session import UserSession
# from .teacher_invitation import SchoolTeacherInvitation
from .auth_factor import AuthFactor
from .klass import Class  # 'class' is a reserved keyword
from .otp_bypass_token import OtpBypassToken
from .school import School
from .session import Session
from .session_auth_factor import SessionAuthFactor
from .student import Student
from .teacher import NonSchoolTeacher, SchoolTeacher, Teacher
from .user import (  # TODO: remove UserProfile
    IndependentUser,
    NonSchoolTeacherUser,
    SchoolTeacherUser,
    StudentUser,
    TeacherUser,
    User,
    UserProfile,
)
