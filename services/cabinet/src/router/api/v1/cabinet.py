from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorCollection

from dependencies.profile import get_profile_id_or_401
from dependencies.store import get_maps_collection
from logger import logging
from schemas.map import MapAndMeta, MapCreate
from schemas.room import NewRoom, RoomMapInfo
from services.map import create_new_map, get_all_maps, get_map_by_id
from services.rooms import create_external_room

cabinet_router = APIRouter(prefix="/cabinet", tags=["cabinet"])
logger = logging.getLogger(__name__)


@cabinet_router.get(
    "/maps/",
    summary="Get all available maps",
    response_description="List of all available maps",
    response_model_by_alias=False,
    response_model=list[MapAndMeta],
)
async def get_maps(
    profile_id: Annotated[int, Depends(get_profile_id_or_401)],
    maps_collection: Annotated[AsyncIOMotorCollection, Depends(get_maps_collection)],
) -> list[MapAndMeta]:
    return await get_all_maps(maps_collection)


@cabinet_router.get(
    "/maps/{pk}",
    summary="Get specific map by ID",
    response_description="Detailed map information",
    response_model_by_alias=False,
    response_model=MapAndMeta,
)
async def get_map(
    pk: str,
    profile_id: Annotated[int, Depends(get_profile_id_or_401)],
    maps_collection: Annotated[AsyncIOMotorCollection, Depends(get_maps_collection)],
) -> MapAndMeta:
    map_data = await get_map_by_id(maps_collection, pk)
    if not map_data:
        raise HTTPException(status_code=404)
    return map_data


@cabinet_router.post(
    "/maps/",
    summary="Create new map",
    response_description="Created map details",
    response_model=MapAndMeta,
    response_model_by_alias=False,
    status_code=status.HTTP_201_CREATED,
)
async def create_map(
    map_model: MapCreate,
    profile_id: Annotated[int, Depends(get_profile_id_or_401)],
    maps_collection: Annotated[AsyncIOMotorCollection, Depends(get_maps_collection)],
) -> MapAndMeta:
    try:
        return await create_new_map(maps_collection, map_model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@cabinet_router.post(
    "/rooms/",
    summary="Create new game room",
    response_description="Created room details",
    response_model=NewRoom,
)
async def create_room(
    room_map_info: RoomMapInfo,
    profile_id: Annotated[int, Depends(get_profile_id_or_401)],
    maps_collection: Annotated[AsyncIOMotorCollection, Depends(get_maps_collection)],
):
    map_data = await get_map_by_id(maps_collection, room_map_info.map_id)
    if not map_data:
        raise HTTPException(status_code=404)

    return await create_external_room(map_data)
