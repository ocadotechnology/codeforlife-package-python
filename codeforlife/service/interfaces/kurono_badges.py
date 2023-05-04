import typing as t

from pydantic import (
    BaseModel,
    Field,
    root_validator,
    PrivateAttr,
)

from ...kurono import schema


class RequestBody(BaseModel):
    class Source(BaseModel):
        code: str = Field()
        _globals: t.Dict[str, t.Any] = PrivateAttr(default_factory=dict)
        _locals: t.Dict[str, t.Any] = PrivateAttr(default_factory=dict)

    source: Source = Field()
    execute: t.Optional[t.Callable[[Source], None]] = Field()

    current_avatar_id: int = Field()
    task_id: t.Optional[int] = Field(ge=1)
    game_state: schema.GameState = Field()

    @root_validator
    def defines_next_turn(cls, request_body: t.Dict[str, t.Any]):
        if "execute" in request_body:
            request_body["execute"](request_body["source"])
        return request_body


class ResponseBody(BaseModel):
    class Report(BaseModel):
        task_id: int = Field(ge=1)

    passed: t.List[Report] = Field()
    failed: t.List[Report] = Field()
    xfailed: t.List[Report] = Field()
    skipped: t.List[Report] = Field()
