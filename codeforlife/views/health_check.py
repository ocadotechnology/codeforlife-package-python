"""
© Ocado Group
Created on 14/11/2024 at 16:31:56(+00:00).
"""

import json
import logging
import os
import typing as t
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property

from django.apps import apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.views.decorators.cache import cache_page
from psutil import Process
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..permissions import AllowAny

if t.TYPE_CHECKING:
    from ..server import Server
    from ..types import Env, JsonDict, JsonList

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
        health: t.Optional[HealthStatus] = None

    health_status: HealthStatus
    additional_info: str
    details: t.Optional[t.List[Detail]] = None


class HealthCheckDetailList(t.List[HealthCheck.Detail]):
    """Builds a list of health-check details with convenience utilities."""

    def __init__(self, server_mode: "Server.Mode"):
        super().__init__()
        self.server_mode = server_mode

    @property
    def health_statuses(self):
        """The health statuses of all the details."""
        return t.cast(
            t.FrozenSet[HealthStatus],
            frozenset(detail.health for detail in self if detail.health),
        )

    def append(  # type: ignore[override]
        self,
        name: str,
        description: str,
        health: t.Optional[HealthStatus] = None,
    ):
        return super().append(
            HealthCheck.Detail(
                name=f"{self.server_mode}.{name}",
                description=description,
                health=health,
            )
        )


class HealthCheckView(APIView):
    """A view for load balancers to determine whether the app is healthy."""

    http_method_names = ["get"]
    permission_classes = [AllowAny]
    startup_timestamp = datetime.now().isoformat()
    cache_timeout: float = 30

    def resolve_health_status(
        self, *health_statuses: HealthStatus
    ) -> HealthStatus:
        """Given 1+ health statuses, resolve the final health status."""
        if len(health_statuses) > 0:
            search_health_statuses: t.List[HealthStatus] = [
                "unhealthy",
                "shuttingDown",
                "startingUp",
            ]
            for search_health_status in search_health_statuses:
                if search_health_status in health_statuses:
                    return search_health_status

            if all(
                health_status == "healthy" for health_status in health_statuses
            ):
                return "healthy"

        return "unknown"

    @cached_property
    def celery_worker(self):
        """The celery worker started by the server."""
        return Process(int(os.environ["SERVER_CELERY_WORKER_PID"]))

    def get_celery_worker_health_check(self) -> HealthCheck:
        """Check the health of the celery worker process."""
        health_check_details = HealthCheckDetailList("celery")

        _status = self.celery_worker.status()
        health_check_details.append(
            name="status",
            description=_status,
            health=(
                "healthy"
                if _status in ["running", "sleeping", "waking", "idle"]
                else "unhealthy"
            ),
        )

        health_check_details.append(
            name="cpu_percent",
            description=str(self.celery_worker.cpu_percent()),
        )

        health_status = self.resolve_health_status(
            *health_check_details.health_statuses
        )

        return HealthCheck(
            health_status=health_status,
            additional_info="[celery] "
            + (
                "All healthy."
                if health_status == "healthy"
                else "Not healthy. See details for more info."
            ),
            details=health_check_details,
        )

    def get_django_worker_health_check(self, request: Request) -> HealthCheck:
        """Check the health of the django worker process."""
        health_check_details = HealthCheckDetailList("django")

        ready = apps.ready
        health_check_details.append(
            name="ready",
            description=str(ready),
            health="healthy" if ready else "startingUp",
        )

        apps_ready = apps.apps_ready
        health_check_details.append(
            name="apps_ready",
            description=str(apps_ready),
            health="healthy" if apps_ready else "startingUp",
        )

        models_ready = apps.models_ready
        health_check_details.append(
            name="models_ready",
            description=str(models_ready),
            health="healthy" if models_ready else "startingUp",
        )

        if settings.DB_ENGINE == "postgresql":

            def check_site_health(health_check_name: str, site_domain: str):
                exists = Site.objects.filter(domain=site_domain).exists()
                health_check_details.append(
                    name=f"site_exists.{health_check_name}",
                    description=str(exists),
                    health="healthy" if exists else "unhealthy",
                )

            if t.cast("Env", settings.ENV) == "local":
                check_site_health(
                    health_check_name="localhost",
                    site_domain=f"localhost:{settings.SERVICE_PORT}",
                )
                check_site_health(
                    health_check_name="ip_address",
                    site_domain=f"127.0.0.1:{settings.SERVICE_PORT}",
                )
            else:
                check_site_health(
                    health_check_name="domain",
                    site_domain=settings.SERVICE_DOMAIN,
                )
                check_site_health(
                    health_check_name="host",
                    site_domain=settings.SERVICE_HOST,
                )

        health_status = self.resolve_health_status(
            *health_check_details.health_statuses
        )

        return HealthCheck(
            health_status=health_status,
            additional_info="[django] "
            + (
                "All healthy."
                if health_status == "healthy"
                else "Not healthy. See details for more info."
            ),
            details=health_check_details,
        )

    def get_health_check(self, request: Request) -> HealthCheck:
        """Check the health of the current service."""
        details: t.List[HealthCheck.Detail] = []

        try:
            django_worker_health_check = self.get_django_worker_health_check(
                request
            )
            health_status = django_worker_health_check.health_status
            additional_info = django_worker_health_check.additional_info
            if django_worker_health_check.details:
                details += django_worker_health_check.details

            if t.cast("Server.Mode", settings.SERVER_MODE) == "celery":
                celery_worker_health_check = (
                    self.get_celery_worker_health_check()
                )
                health_status = self.resolve_health_status(
                    health_status,
                    celery_worker_health_check.health_status,
                )
                additional_info += celery_worker_health_check.additional_info
                if celery_worker_health_check.details:
                    details += celery_worker_health_check.details

            return HealthCheck(
                health_status=health_status,
                additional_info=additional_info,
                details=details,
            )
        # pylint: disable-next=broad-exception-caught
        except Exception as ex:
            return HealthCheck(
                health_status="unknown",
                additional_info=str(ex),
                details=details,
            )

    def get(self, request: Request):
        """Return a health check for the current service."""
        health_check = self.get_health_check(request)

        data: JsonDict = {
            "appId": settings.APP_ID,
            "healthStatus": health_check.health_status,
            "lastCheckedTimestamp": datetime.now().isoformat(),
            "additionalInformation": health_check.additional_info,
            "startupTimestamp": self.startup_timestamp,
            "appVersion": settings.APP_VERSION,
        }

        if health_check.details:
            details: JsonList = []
            for _detail in health_check.details:
                detail: JsonDict = {
                    "name": _detail.name,
                    "description": _detail.description,
                }
                if _detail.health:
                    detail["health"] = _detail.health

                details.append(detail)

            data["details"] = details

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
