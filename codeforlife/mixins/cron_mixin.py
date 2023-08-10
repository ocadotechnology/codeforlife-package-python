from ..permissions import IsCronRequestFromGoogle


class CronMixin:
    """
    A cron job on Google's AppEngine.
    https://cloud.google.com/appengine/docs/flexible/scheduling-jobs-with-cron-yaml
    """

    http_method_names = ["get"]
    permission_classes = [IsCronRequestFromGoogle]
