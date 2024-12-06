"""
© Ocado Group
Created on 12/04/2024 at 16:51:36(+01:00).
"""

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..permissions import AllowAny


class CsrfCookieView(APIView):
    """A view to get a CSRF cookie."""

    http_method_names = ["get"]
    permission_classes = [AllowAny]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request: Request):
        """
        Return a response which Django will auto-insert a CSRF cookie into.
        """
        return Response()
