from enum import IntEnum, StrEnum


class GameStatus(IntEnum):
    WAITING_FOR_PLAYERS = 1
    IN_PROGRESS = 2
    FINISHED = 3


class PlayerStatus(StrEnum):
    NOT_READY = "not_ready"
    READY = "ready"
    LOSER = "lose"
    WINNER = "win"
    STOPPED = "stop"
