"""
© Ocado Group
Created on 14/03/2024 at 12:14:41(+00:00).
"""

# NOTE: Need to import signals so they are discoverable by Django.
from .auth_factor import auth_factor__post_delete
from .teacher import teacher_receiver
from .user import user_receiver
