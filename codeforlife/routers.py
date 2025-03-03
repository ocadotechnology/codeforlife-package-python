"""
© Ocado Group
Created on 03/03/2025 at 13:30:54(+00:00).
"""

from rest_framework.routers import DefaultRouter as _DefaultRouter

from .views import APIRootView


class DefaultRouter(_DefaultRouter):
    """Set custom api-root view."""

    APIRootView = APIRootView


default_router = DefaultRouter()
