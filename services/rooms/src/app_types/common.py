from enum import IntEnum, StrEnum, auto


class GameStatus(IntEnum):
    WAITING_FOR_PLAYERS = auto()
    IN_PROGRESS = auto()
    FINISHED = auto()


class PlayerStatus(StrEnum):
    NOT_READY = "not_ready"
    READY = "ready"
    LOSER = "lose"
    WINNER = "win"
    STOPPED = "stop"
