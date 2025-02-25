"""
© Ocado Group
Created on 12/04/2024 at 16:53:52(+01:00).

This file manages Django but also acts a settings file.
"""

# pylint: disable-next=wildcard-import,unused-wildcard-import
from codeforlife.settings import *

# NOTE: This is only used locally for testing purposes.
SECRET_KEY = "XTgWqMlZCMI_E5BvCArkif9nrJIIhe_6Ic6Q_UcWJDk="

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "codeforlife.user",
    "game",  # TODO: remove this
    "common",  # TODO: remove this
    "portal",  # TODO: remove this
]

MIDDLEWARE = [
    "codeforlife.middlewares.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "codeforlife.user.urls"

if __name__ == "__main__":
    import os
    import sys

    from django.core.management import execute_from_command_line

    # Set the path of the settings file to the path of this file.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", Path(__file__).stem)

    execute_from_command_line(sys.argv)
