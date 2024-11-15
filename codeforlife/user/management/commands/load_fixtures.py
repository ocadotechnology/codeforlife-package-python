"""
© Ocado Group
Created on 10/06/2024 at 10:44:45(+01:00).
"""

from ....commands import LoadFixtures


# pylint: disable-next=missing-class-docstring
class Command(LoadFixtures):
    required_app_labels = {"user"}
