from pydantic import BaseModel


class NewRoom(BaseModel):
    room_key: str
