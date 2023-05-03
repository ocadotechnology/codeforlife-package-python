import typing as t
from inspect import signature

from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    validator,
)

from ...kurono import (
    schema,
    direction,
    location,
    MoveAction,
    PickupAction,
    WaitAction,
    MoveTowardsAction,
    DropAction,
)


class Source(BaseModel):
    code: str = Field()
    _globals: t.Dict[str, t.Any] = PrivateAttr(
        default_factory=lambda: {
            "direction": direction,
            "location": location,
            "MoveAction": MoveAction,
            "PickupAction": PickupAction,
            "WaitAction": WaitAction,
            "MoveTowardsAction": MoveTowardsAction,
            "DropAction": DropAction,
        }
    )
    _locals: t.Dict[str, t.Any] = PrivateAttr(default_factory=dict)


class KuronoBadges(BaseModel):
    source: Source = Field()
    current_avatar_id: int = Field()
    task_id: t.Optional[int] = Field(ge=1)
    game_state: schema.GameState = Field()

    @validator("source")
    def defines_next_turn(cls, source: Source):
        exec(source.code, source._globals, source._locals)
        for key in [key for key in source._locals.keys() if key != "next_turn"]:
            source._globals[key] = source._locals.pop(key)

        next_turn = source._locals.get("next_turn")
        if not next_turn:
            raise ValueError("next_turn is not defined")
        if not callable(next_turn):
            raise ValueError("next_turn is not a callable")

        next_turn_parameters = signature(next_turn).parameters
        if len(next_turn_parameters) != 2:
            raise ValueError("next_turn expected 2 parameters")
        if list(next_turn_parameters.keys()) != ["world_state", "avatar_state"]:
            raise ValueError("next_turn has the wrong named parameters")

        return source
