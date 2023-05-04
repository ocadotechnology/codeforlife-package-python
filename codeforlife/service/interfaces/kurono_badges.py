import typing as t
from inspect import signature

from pydantic import (
    BaseModel,
    Field,
    validator,
)

from ...kurono import schema


class RequestBody(BaseModel):
    class Source(BaseModel):
        code: str = Field()
        globals: t.Optional[t.Dict[str, t.Any]] = Field()
        locals: t.Optional[t.Dict[str, t.Any]] = Field()

        @validator("locals")
        def defines_next_turn(cls, locals: t.Dict[str, t.Any]):
            next_turn = locals.get("next_turn")
            if not next_turn:
                raise ValueError("next_turn is not defined")
            if not callable(next_turn):
                raise ValueError("next_turn is not a callable")

            next_turn_parameters = signature(next_turn).parameters
            if len(next_turn_parameters) != 2:
                raise ValueError("next_turn expected 2 parameters")
            if list(next_turn_parameters.keys()) != ["world_state", "avatar_state"]:
                raise ValueError("next_turn has the wrong named parameters")

            return locals

    source: Source = Field()
    current_avatar_id: int = Field()
    task_id: t.Optional[int] = Field(ge=1)
    game_state: schema.GameState = Field()


class ResponseBody(BaseModel):
    class Report(BaseModel):
        task_id: int = Field(ge=1)

    passed: t.List[Report] = Field()
    failed: t.List[Report] = Field()
    xfailed: t.List[Report] = Field()
    skipped: t.List[Report] = Field()
