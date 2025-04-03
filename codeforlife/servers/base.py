"""
© Ocado Group
Created on 31/03/2025 at 09:04:19(+01:00).
"""

import os
import sys

MAIN_MODULE = os.path.splitext(os.path.basename(sys.argv[0]))[0]


class BaseServer:
    """The base server which all servers must inherit."""

    # The dot-path of the application module.
    app_module: str = "application"
    # The dot-path of Django's manage module.
    django_manage_module: str = "manage"

    @classmethod
    def app_server_is_running(cls):
        """Whether or not the app server is module."""
        return MAIN_MODULE == cls.app_module

    @classmethod
    def django_dev_server_is_running(cls):
        """Whether or not the Django development server is running."""
        return (
            MAIN_MODULE == cls.django_manage_module
            and sys.argv[1] == "runserver"
        )
