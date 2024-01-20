"""
© Ocado Group
Created on 20/01/2024 at 09:52:43(+00:00).
"""

from rest_framework.test import APIClient, APITestCase


class CronClient(APIClient):
    """Base client for all CRON jobs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, HTTP_X_APPENGINE_CRON="true")


class CronTestCase(APITestCase):
    """Base test case for all CRON jobs."""

    client: CronClient
    client_class = CronClient
