import typing as t

from flask import request, Response
from pydantic import BaseModel, ValidationError


def handle_flask_request(run: t.Callable[..., BaseModel]):
    try:
        response_body: BaseModel = run(**request.json)
        return Response(
            response_body.json(),
            status=200,
            content_type="application/json",
        )
    except ValidationError as error:
        return Response(
            error.json(),
            status=400,
            content_type="application/json",
        )
    except Exception as ex:
        return Response(
            str(ex),
            status=500,
            content_type="text/plain",
        )
