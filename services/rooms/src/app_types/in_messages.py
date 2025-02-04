from typing import Literal, TypedDict


class AuthMessage(TypedDict):
    at: Literal["auth"]
    token: str


class ReadyMessage(TypedDict):
    at: Literal["ready"]


class PointDict(TypedDict):
    row: int
    col: int


class MoveMessage(TypedDict):
    at: Literal["move"]
    previous: PointDict
    current: PointDict


class ColorMessage(TypedDict):
    at: Literal["color"]
    color: int
