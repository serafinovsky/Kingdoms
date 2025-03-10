from typing import Literal, NotRequired, TypedDict

from app_types.common import PlayerStatus
from app_types.map import GameMap


class PlayerData(TypedDict):
    id: int
    username: str
    color: int
    status: PlayerStatus


class PlayersMessage(TypedDict):
    at: Literal["players"]
    players: list[PlayerData]


class AuthConfirmMessage(TypedDict):
    at: Literal["auth"]
    status: bool


class StartMessage(TypedDict):
    at: Literal["start"]


class PointDict(TypedDict):
    row: int
    col: int


class GameStat(TypedDict):
    fields: int
    power: int


class UpdateMessage(TypedDict):
    at: Literal["update"]
    map: GameMap
    turn: int
    stat: tuple[PlayerData, GameStat]
    cursor: NotRequired[PointDict]
    prev_cursor: NotRequired[PointDict]
