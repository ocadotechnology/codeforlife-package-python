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
        # Django's default behavior with the @login_required decorator is to
        # redirect users to the login template found in setting LOGIN_URL.
        # Because we're using a React frontend, we want to return a
        # 401-Unauthorized whenever a user's session-cookie expires so we can
        # redirect them to the login page. Therefore, all login redirects will
        # direct to this view which will return the desired 401.
        path(
            "api/session/expired/",
            lambda request: HttpResponse(
                status=status.HTTP_401_UNAUTHORIZED,
            ),
            name="session-expired",
        ),
        path(
            "api/",
            include("codeforlife.user.urls"),
            name="user",
        ),
        path(
            "api/",
            include(api_urls_path),
            name="api",
        ),
        re_path(
            r"^(?!api/).*",
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
            rf"^(?!{SERVICE_NAME}/).*",
            lambda request: HttpResponse(
                f'The base route is "{SERVICE_NAME}/".',
                status=status.HTTP_404_NOT_FOUND,
            ),
            name="service-not-found",
        ),
    ]
