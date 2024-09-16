"""
© Ocado Group
Created on 16/09/2024 at 15:19:54(+01:00).

Custom error handlers which override django's default behavior to render a
template.

https://docs.djangoproject.com/en/3.2/ref/urls/#module-django.conf.urls
"""

from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    HttpResponseServerError,
)

# pylint: disable=unnecessary-lambda-assignment
handler400 = lambda request, template: HttpResponseBadRequest()
handler403 = lambda request, template: HttpResponseForbidden()
handler404 = lambda request, template: HttpResponseNotFound()
handler500 = lambda request: HttpResponseServerError()
# pylint: enable=unnecessary-lambda-assignment
