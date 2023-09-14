from rest_framework.request import Request
from rest_framework.response import Response

from ..permissions import IsCronRequestFromGoogle


class CronMixin:
    """
    A cron job on Google's AppEngine.
    https://cloud.google.com/appengine/docs/flexible/scheduling-jobs-with-cron-yaml
    """

    http_method_names = ["get"]
    permission_classes = [IsCronRequestFromGoogle]

    def get(self, request: Request) -> Response:
        raise NotImplementedError()
