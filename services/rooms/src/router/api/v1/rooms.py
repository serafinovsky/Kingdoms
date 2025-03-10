from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from redis.asyncio import Redis

from app_types.room import LobbyRoom
from dependencies.store import get_redis_client
from repositories.room import lobby_repo
from schemas.map import MapAndMeta as MapAndMetaModel
from schemas.room import NewRoom
from services.room import room_manager

rooms_router = APIRouter(prefix="/rooms")


@rooms_router.post("/", status_code=status.HTTP_201_CREATED, response_model=NewRoom)
async def create_room(
    map_and_meta: MapAndMetaModel,
    redis: Annotated[Redis, Depends(get_redis_client)],
):
    room_key = await room_manager.save_room(
        redis, {"map": map_and_meta.map, "meta": map_and_meta.meta}
    )
    return NewRoom(room_key=room_key)


@rooms_router.get("/", response_model=list[LobbyRoom])
async def get_rooms(
    redis: Annotated[Redis, Depends(get_redis_client)],
    limit: int = Query(50, ge=1, le=50, description="Pagination limit"),
) -> list[LobbyRoom]:
    """Get sorted list of available rooms"""
    return await lobby_repo.get_rooms(redis, limit=limit)
