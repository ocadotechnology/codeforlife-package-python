"""
© Ocado Group
Created on 06/12/2024 at 11:55:49(+00:00).

Session views.
"""

from django.contrib.auth.views import LogoutView as _LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework import status


class LogoutView(_LogoutView):
    """Override Django's logout view to always return a JSON response."""

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse({})


def session_expired_view(request: HttpRequest):
    """
    Django's default behavior with the @login_required decorator is to redirect
    users to the login template found in setting LOGIN_URL. Because we're using
    a React frontend, we want to return a 401-Unauthorized whenever a user's
    session-cookie expires so we can redirect them to the login page. Therefore,
    all login redirects will direct to this view which will return the desired
    401.
    """

    return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
