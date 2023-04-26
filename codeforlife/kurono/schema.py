# TODO: replace objects with these.
import typing as t
from enum import Enum

from pydantic import BaseModel, Field


class Location(BaseModel):
    x: int = Field(ge=-15, le=15)
    y: int = Field(ge=-15, le=15)


class Orientation(str, Enum):
    north = "north"
    east = "east"
    south = "south"
    west = "west"


class Worksheet:
    class Era(str, Enum):
        future = "future"
        ancient = "ancient"
        modern = "modern"


class Artefact(BaseModel):
    class Type(str, Enum):
        chest = "chest"
        key = "key"
        yellow_orb = "yellow_orb"
        phone = "phone"
        keyboard = "keyboard"
        coins = "coins"

    type: Type = Field()


class Avatar(BaseModel):
    location: Location = Field()
    id: int = Field()
    orientation: Orientation = Field()
    backpack: t.Optional[t.List[Artefact]] = Field()


class Interactable(BaseModel):
    class Type(str, Enum):
        score = "score"
        damage_boost = "damage_boost"
        health = "health"
        invulnerability = "invulnerability"

    type: t.Union[Type, Artefact.Type] = Field()
    location: Location = Field()


class Obstacle(BaseModel):
    location: Location = Field()
    texture: int = Field()


class GameState(BaseModel):
    era: Worksheet.Era = Field()
    worksheetID: int = Field(ge=1, le=4)
    southWestCorner: Location = Field()
    northEastCorner: Location = Field()
    players: t.List[Avatar] = Field()
    interactables: t.List[Interactable] = Field()
    obstacles: t.List[Obstacle] = Field()
    turnCount: int = Field(ge=0)
