"""
© Ocado Group
Created on 14/11/2024 at 16:31:56(+00:00).
"""

import json
import logging
import typing as t
from dataclasses import dataclass
from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..permissions import AllowAny

HealthStatus = t.Literal[
    "healthy",
    "startingUp",
    "shuttingDown",
    "unhealthy",
    "unknown",
]


@dataclass(frozen=True)
class HealthCheck:
    """The health of the current service."""

    @dataclass(frozen=True)
    class Detail:
        """A health detail."""

        name: str
        description: str
        health: HealthStatus

    health_status: HealthStatus
    additional_info: str
    details: t.Optional[t.List[Detail]] = None


class HealthCheckView(APIView):
    """A view for load balancers to determine whether the app is healthy."""

    http_method_names = ["get"]
    permission_classes = [AllowAny]
    startup_timestamp = datetime.now().isoformat()
    cache_timeout: float = 30

    def get_health_check(self, request: Request) -> HealthCheck:
        """Check the health of the current service."""
        try:
            if not apps.ready or not apps.apps_ready or not apps.models_ready:
                return HealthCheck(
                    health_status="startingUp",
                    additional_info="Apps not ready.",
                )

            host = request.get_host()
            if not Site.objects.filter(domain=host).exists():
                # TODO: figure out how to dynamically get and set site.
                # return HealthCheck(
                #     health_status="unhealthy",
                #     additional_info=f'Site "{host}" does not exist.',
                # )
                logging.warning('Site "%s" does not exist.', host)

            return HealthCheck(
                health_status="healthy",
                additional_info="All healthy.",
            )
        # pylint: disable-next=broad-exception-caught
        except Exception as ex:
            return HealthCheck(
                health_status="unknown",
                additional_info=str(ex),
            )

    def get(self, request: Request):
        """Return a health check for the current service."""
        health_check = self.get_health_check(request)

        data = {
            "appId": settings.APP_ID,
            "healthStatus": health_check.health_status,
            "lastCheckedTimestamp": datetime.now().isoformat(),
            "additionalInformation": health_check.additional_info,
            "startupTimestamp": self.startup_timestamp,
            "appVersion": settings.APP_VERSION,
            "details": [
                {
                    "name": detail.name,
                    "description": detail.description,
                    "health": detail.health,
                }
                for detail in (health_check.details or [])
            ],
        }

        if health_check.health_status != "healthy":
            logging.warning("health check: %s", json.dumps(data))

        return Response(
            data,
            status={
                # The app is running normally.
                "healthy": status.HTTP_200_OK,
                # The app is performing app-specific initialisation which must
                # complete before it will serve normal application requests
                # (perhaps the app is warming a cache or something similar). You
                # only need to use this status if your app will be in a start-up
                # mode for a prolonged period of time.
                "startingUp": status.HTTP_503_SERVICE_UNAVAILABLE,
                # The app is shutting down. As with startingUp, you only need to
                # use this status if your app takes a prolonged amount of time
                # to shutdown, perhaps because it waits for a long-running
                # process to complete before shutting down.
                "shuttingDown": status.HTTP_503_SERVICE_UNAVAILABLE,
                # The app is not running normally.
                "unhealthy": status.HTTP_503_SERVICE_UNAVAILABLE,
                # The app is not able to report its own state.
                "unknown": status.HTTP_503_SERVICE_UNAVAILABLE,
            }[health_check.health_status],
        )

    @classmethod
    def as_view(cls, **initkwargs):
        return cache_page(cls.cache_timeout)(super().as_view(**initkwargs))
