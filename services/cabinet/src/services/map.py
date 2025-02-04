from collections import defaultdict

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app_types.map import CellType, GameMap, MapMeta, Point
from schemas.map import MapAndMeta, MapAndMetaCreate, MapCreate


async def get_all_maps(maps_collection: AsyncIOMotorCollection) -> list[MapAndMeta]:
    items = await maps_collection.find().to_list()
    return [MapAndMeta(**item) for item in items]


async def get_map_by_id(maps_collection: AsyncIOMotorCollection, map_id: str) -> MapAndMeta | None:
    item = await maps_collection.find_one({"_id": ObjectId(map_id), "meta.version": 1})
    return MapAndMeta(**item) if item else None


def validate_map_dimensions(game_map: GameMap) -> None:
    if len(game_map) > 32 or len(game_map) < 4:
        raise ValueError("Map height must be between 4 and 32")

    rows = set(len(row) for row in game_map)
    if not rows or len(rows) > 1:
        raise ValueError("All rows must have the same length")

    row_len = rows.pop()
    if row_len > 32 or row_len < 4:
        raise ValueError("Map width must be between 4 and 32")


def create_map_meta(game_map: GameMap) -> MapMeta:
    meta: MapMeta = {"version": 1, "points_of_interest": defaultdict(list)}

    for r, row in enumerate(game_map):
        for c, col in enumerate(row):
            cell_type = col["type"]
            if cell_type in [CellType.CASTLE, CellType.SPAWN]:
                meta["points_of_interest"][cell_type].append(Point(r, c))

    max_players = len(meta["points_of_interest"][CellType.SPAWN])
    if max_players < 2:
        raise ValueError("Map must have at least 2 spawn points")

    return meta


async def create_new_map(
    maps_collection: AsyncIOMotorCollection,
    map_model: MapCreate,
) -> MapAndMeta:
    game_map = map_model.map

    validate_map_dimensions(game_map)
    meta = create_map_meta(game_map)

    map_and_meta = MapAndMetaCreate(map=game_map, meta=meta)
    insert_result = await maps_collection.insert_one(map_and_meta.model_dump())

    new_map = await maps_collection.find_one({"_id": insert_result.inserted_id})
    if not new_map:
        raise ValueError("Failed to create new map")

    return MapAndMeta(**new_map)
