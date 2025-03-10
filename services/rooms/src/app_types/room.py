from typing import TypedDict


class LobbyRoom(TypedDict):
    name: str
    max_players: int
    current_players: int
