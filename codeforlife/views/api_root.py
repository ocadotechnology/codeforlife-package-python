"""
© Ocado Group
Created on 03/03/2025 at 13:31:53(+00:00).
"""

from rest_framework.routers import APIRootView as _APIRootView

from ..permissions import AllowAny


class APIRootView(_APIRootView):
    """Allow anyone to see the api-root view."""

    permission_classes = [AllowAny]
