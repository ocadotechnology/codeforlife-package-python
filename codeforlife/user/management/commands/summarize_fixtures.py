"""
© Ocado Group
Created on 22/02/2024 at 09:24:27(+00:00).
"""

from ....commands import SummarizeFixtures


# pylint: disable-next=missing-class-docstring
class Command(SummarizeFixtures):
    required_app_labels = {"user"}
