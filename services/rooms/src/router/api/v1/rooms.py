from typing import Annotated

from fastapi import APIRouter, Depends, status
from redis.asyncio import Redis

from dependencies.store import get_redis_client
from schemas.map import MapAndMeta as MapAndMetaModel
from schemas.room import NewRoom
from services.room import room_manager

rooms_router = APIRouter(prefix="/rooms")


@rooms_router.post("/", status_code=status.HTTP_201_CREATED, response_model=NewRoom)
async def create_room(
    map_and_meta: MapAndMetaModel,
    redis: Annotated[Redis, Depends(get_redis_client)],
):
    room_key = await room_manager.init_room(
        redis, {"map": map_and_meta.map, "meta": map_and_meta.meta}
    )
    return NewRoom(room_key=room_key)
