"""
© Ocado Group
Created on 12/04/2024 at 14:42:20(+01:00).
"""

import typing as t

from django.conf import settings
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path, re_path

from ..views import (
    CsrfCookieView,
    HealthCheckView,
    LogoutView,
    path_not_found_view,
    session_expired_view,
)

UrlPatterns = t.List[t.Union[URLResolver, URLPattern]]


def get_urlpatterns(
    api_url_patterns: UrlPatterns,
    health_check_view: t.Type[HealthCheckView] = HealthCheckView,
    include_user_urls: bool = True,
) -> UrlPatterns:
    """Generate standard url patterns for each service.

    Args:
        api_urls_path: The path to the api's urls.
        health_check_view: The health check view to use.
        include_user_urls: Whether or not to include the CFL's user urls.

    Returns:
        The standard url patterns for each service.
    """

    urlpatterns: UrlPatterns = [
        path(
            "health-check/",
            health_check_view.as_view(),
            name="health-check",
        ),
    ]

    path_not_found_pattern = re_path(
        r"^(?P<path>.*)$",
        path_not_found_view,
        name="path-not-found",
    )

    if settings.SERVER_MODE == "celery":
        urlpatterns.append(path_not_found_pattern)
        return urlpatterns

    urlpatterns += [
        # https://www.django-rest-framework.org/topics/browsable-api/#authentication
        path(
            "/",
            include("rest_framework.urls", namespace="rest_framework"),
        ),
        path(
            "admin/",
            admin.site.urls,
            name="admin",
        ),
        path(
            "csrf/cookie/",
            CsrfCookieView.as_view(),
            name="get-csrf-cookie",
        ),
        path(
            "session/logout/",
            LogoutView.as_view(),
            name="logout",
        ),
        path(
            "session/expired/",
            session_expired_view,
            name="session-expired",
        ),
        *api_url_patterns,
    ]

    if include_user_urls:
        urlpatterns.append(
            path(
                "",
                include("codeforlife.user.urls"),
                name="user",
            )
        )

    urlpatterns.append(path_not_found_pattern)
    return urlpatterns
