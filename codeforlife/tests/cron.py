from .api import APIClient, APITestCase


class CronTestClient(APIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, HTTP_X_APPENGINE_CRON="true")


class CronTestCase(APITestCase):
    client: CronTestClient
    client_class = CronTestClient
