from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import include, path, re_path
from rest_framework import status

from .settings import SERVICE_IS_ROOT, SERVICE_NAME
from .views import csrf


def service_urlpatterns(
    api_urls_path: str = "api.urls",
    frontend_template_name: str = "frontend.html",
):
    urlpatterns = [
        path(
            "admin/",
            admin.site.urls,
            name="admin",
        ),
        path(
            "api/csrf/cookie/",
            csrf.CookieView.as_view(),
            name="get-csrf-cookie",
        ),
        path(
            "api/session/logout/",
            LogoutView.as_view(),
            name="logout",
        ),
        path(
            "api/",
            include(api_urls_path),
            name="api",
        ),
        re_path(
            r"^api/.*",
            lambda request: HttpResponse(
                "API endpoint not found",
                status=status.HTTP_404_NOT_FOUND,
            ),
            name="api-endpoint-not-found",
        ),
        re_path(
            r".*",
            lambda request: render(request, frontend_template_name),
            name="frontend",
        ),
    ]

    if SERVICE_IS_ROOT:
        return urlpatterns

    return [
        path(
            f"{SERVICE_NAME}/",
            include(urlpatterns),
            name="service",
        ),
        re_path(
            r".*",
            lambda request: HttpResponse(
                f'The base route is "{SERVICE_NAME}/".',
                status=status.HTTP_404_NOT_FOUND,
            ),
            name="service-not-found",
        ),
    ]
