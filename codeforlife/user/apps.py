"""
© Ocado Group
Created on 14/03/2024 at 12:22:40(+00:00).
"""

from django.apps import AppConfig


# pylint: disable-next=missing-class-docstring
class UserConfig(AppConfig):
    name = "codeforlife.user"

    def ready(self):
        # NOTE: Need to import signals so they are discoverable by Django.
        # pylint: disable-next=import-outside-toplevel,unused-import
        from . import signals
