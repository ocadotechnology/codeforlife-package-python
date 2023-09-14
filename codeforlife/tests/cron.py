from rest_framework.test import APIClient, APITestCase


class CronTestClient(APIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, HTTP_X_APPENGINE_CRON="true")

    def generic(
        self,
        method,
        path,
        data="",
        content_type="application/octet-stream",
        secure=False,
        **extra,
    ):
        wsgi_response = super().generic(
            method, path, data, content_type, secure, **extra
        )
        assert (
            200 <= wsgi_response.status_code < 300
        ), f"Response has error status code: {wsgi_response.status_code}"

        return wsgi_response


class CronTestCase(APITestCase):
    client_class = CronTestClient
