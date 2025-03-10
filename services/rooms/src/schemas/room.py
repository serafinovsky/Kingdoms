from pydantic import BaseModel


class NewRoom(BaseModel):
    room_key: str


class Room(BaseModel):
    name: str
    max_players: int
    current_players: int
