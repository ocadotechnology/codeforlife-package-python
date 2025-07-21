"""
© Ocado Group
Created on 16/09/2024 at 15:19:54(+01:00).

Custom error handlers which override django's default behavior to render a
template.

https://docs.djangoproject.com/en/5.1/ref/urls/#module-django.conf.urls
"""

from django.http import (
    HttpRequest,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
)

# pylint: disable=unused-argument


def handler400(request: HttpRequest, exception: Exception):
    """The view called when a request was malformed."""
    return HttpResponseBadRequest()


def handler403(request: HttpRequest, exception: Exception):
    """The view called when access to a view is forbidden."""
    return HttpResponseForbidden()


def handler404(request: HttpRequest, exception: Exception):
    """The view called when no matching view was found for a path."""
    return HttpResponseNotFound(
        f'No matching view for "{request.META["PATH_INFO"]}".'
    )


def handler500(request: HttpRequest):
    """The view called when a generic error occurs."""
    return HttpResponseServerError()
