"""
© Ocado Group
Created on 05/02/2024 at 16:33:52(+00:00).
"""

from rest_framework.views import APIView as _APIView

from ..request import Request


# pylint: disable-next=missing-class-docstring
class APIView(_APIView):
    request: Request

    def initialize_request(self, request, *args, **kwargs):
        # NOTE: Call to super has side effects and is required.
        super().initialize_request(request, *args, **kwargs)

        return Request(
            request,
            parsers=self.get_parsers(),
            authenticators=self.get_authenticators(),
            negotiator=self.get_content_negotiator(),
            parser_context=self.get_parser_context(request),
        )
