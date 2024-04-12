"""
© Ocado Group
Created on 12/04/2024 at 14:36:41(+01:00).
"""

from rest_framework.request import Request
from rest_framework.response import Response

from ..permissions import IsCronRequestFromGoogle


# pylint: disable-next=too-few-public-methods
class CronMixin:
    """
    A cron job on Google's AppEngine.
    https://cloud.google.com/appengine/docs/flexible/scheduling-jobs-with-cron-yaml
    """

    http_method_names = ["get"]
    permission_classes = [IsCronRequestFromGoogle]

    def get(self, request: Request) -> Response:
        """Handle the CRON request."""
        raise NotImplementedError()
