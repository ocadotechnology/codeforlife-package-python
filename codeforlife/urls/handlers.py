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

handler400 = lambda request: HttpResponseBadRequest()
handler403 = lambda request: HttpResponseForbidden()
handler404 = lambda request: HttpResponseNotFound()
handler500 = lambda request: HttpResponseServerError()
