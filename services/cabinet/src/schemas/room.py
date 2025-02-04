from pydantic import BaseModel, ConfigDict

from app_types.common import PyObjectId


class RoomMapInfo(BaseModel):
    map_id: PyObjectId

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class NewRoom(BaseModel):
    room_key: str
