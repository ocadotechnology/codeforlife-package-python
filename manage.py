"""
© Ocado Group
Created on 12/04/2024 at 16:53:52(+01:00).

This file manages manages Django but also acts a settings file.
"""

from pathlib import Path

# pylint: disable-next=wildcard-import,unused-wildcard-import
from codeforlife.settings import *

BASE_DIR = Path(__file__).resolve().parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "codeforlife.user",
    "aimmo",  # TODO: remove this
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

DATABASES = get_databases(BASE_DIR)

if __name__ == "__main__":
    import os
    import sys

    from django.core.management import execute_from_command_line

    # Set the path of the settings file to the path of this file.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", Path(__file__).stem)

    execute_from_command_line(sys.argv)
