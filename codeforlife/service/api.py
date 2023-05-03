import typing as t

from flask import request, Response
from pydantic import BaseModel, ValidationError


RequestBody = t.TypeVar("RequestBody", bound=BaseModel)
ResponseBody = t.TypeVar("ResponseBody", bound=BaseModel)


def handle_flask_request(
    request_body_type: t.Type[RequestBody],
    run: t.Callable[[RequestBody], ResponseBody],
):
    try:
        request_body = request_body_type(**request.json)
    except ValidationError as error:
        return Response(error.json(), status=400, content_type="application/json")

    try:
        response_body = run(request_body)
    except Exception as ex:
        return Response(str(ex), status=500, content_type="text/plain")

    return Response(response_body.json(), status=200, content_type="application/json")
