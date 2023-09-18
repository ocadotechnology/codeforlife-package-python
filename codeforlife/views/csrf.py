from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class CookieView(APIView):
    http_method_names = ["get"]

    @method_decorator(ensure_csrf_cookie)
    def get(self, request: Request):
        return Response()
