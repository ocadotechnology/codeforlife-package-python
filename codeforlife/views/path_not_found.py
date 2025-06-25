"""
© Ocado Group
Created on 25/06/2025 at 14:47:56(+01:00).
"""

from django.http import HttpRequest, HttpResponse
from rest_framework import status


def path_not_found_view(request: HttpRequest, path: str):
    """The view called when no matching view was found for a path."""
    return HttpResponse(
        f'No matching view for "{path}".',
        status=status.HTTP_404_NOT_FOUND,
    )
