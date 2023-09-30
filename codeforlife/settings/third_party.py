"""
This file contains custom settings defined by third party extensions.
"""

from .django import DEBUG

# CORS
# https://pypi.org/project/django-cors-headers/

CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = ["https://www.codeforlife.education"]
