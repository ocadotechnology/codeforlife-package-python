import typing as t

from flask import request, Response
from pydantic import BaseModel, ValidationError


RequestJson = t.Dict[str, t.Any]
RequestBody = t.TypeVar("RequestBody", bound=BaseModel)
ResponseBody = t.TypeVar("ResponseBody", bound=BaseModel)


def validate_flask_request_json(
    request_body_type: t.Type[RequestBody],
    request_json: RequestJson,
):
    try:
        return request_body_type(**request_json)
    except ValidationError as error:
        return Response(error.json(), status=400, content_type="application/json")


def handle_flask_request(
    run: t.Callable[[RequestBody], ResponseBody],
    request_body_type: t.Type[RequestBody],
    request_json: RequestJson = None,
):
    request_json = request_json or request.json

    request_body_or_response = validate_flask_request_json(request_body_type, request_json)
    if isinstance(request_body_or_response, Response):
        return request_body_or_response

    try:
        response_body = run(request_body_or_response)
    except Exception as ex:
        return Response(str(ex), status=500, content_type="text/plain")

    return Response(response_body.json(), status=200, content_type="application/json")
