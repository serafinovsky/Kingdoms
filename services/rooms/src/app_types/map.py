from enum import StrEnum
from typing import Literal, NamedTuple, NotRequired, TypedDict


class CellType(StrEnum):
    SPAWN = "spawn"
    KING = "king"
    BLOCKER = "block"
    FIELD = "field"
    CASTLE = "castle"


class Cell(TypedDict):
    type: NotRequired[CellType]
    player: NotRequired[int]
    power: NotRequired[int]


class Point(NamedTuple):
    row: int
    col: int


class MapMeta(TypedDict):
    points_of_interest: dict[CellType, list[Point]]
    version: Literal[1]


GameMap = list[list[Cell]]


class MapAndMeta(TypedDict):
    map: GameMap
    meta: MapMeta
