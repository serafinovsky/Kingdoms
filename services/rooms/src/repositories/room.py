import json
from typing import Any, TypeVar, cast

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app_types.map import MapAndMeta, Point
from settings import settings
from utils import make_room_key

JsonType = str | int | float | bool | None | dict[str, Any] | list[Any]
T = TypeVar("T")


class RoomError(Exception):
    """Base exception for room-related errors"""


class RoomNotFoundError(RoomError):
    """Raised when room is not found in Redis"""


class RoomSerializationError(RoomError):
    """Raised when room serialization/deserialization fails"""


class MapAndMetaEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling MapAndMeta and Point objects"""

    def default(self, o: object) -> JsonType:
        if isinstance(o, Point):
            return {"row": o.row, "col": o.col, "type": "Point"}
        return super().default(o)

    def encode(self, o: object) -> str:
        def hint_tuples(item: Any) -> JsonType:
            if isinstance(item, Point):
                return self.default(item)
            elif isinstance(item, (list, tuple)):
                return [hint_tuples(e) for e in item]
            elif isinstance(item, dict):
                return {key: hint_tuples(value) for key, value in item.items()}
            return item

        return super().encode(hint_tuples(o))


def map_and_meta_deserializer(obj: dict[str, Any]) -> Point | dict[str, Any]:
    """Deserialize JSON objects into Point instances or plain dictionaries"""
    if (
        isinstance(obj, dict)
        and all(k in obj for k in ("row", "col", "type"))
        and obj["type"] == "Point"
    ):
        return Point(row=obj["row"], col=obj["col"])
    return obj


class RoomRepo:
    """Repository class for managing room data in Redis"""

    def __init__(self) -> None:
        self._pk_prefix: str = "__pk:rooms"
        self._room_prefix: str = "__rooms:"

    async def _get_next_id(self, redis: Redis) -> int:
        try:
            return await redis.incr(self._pk_prefix)
        except RedisError as e:
            raise RoomError(f"Failed to generate room ID: {e}") from e

    def _make_key(self, room_key: str) -> str:
        return f"{self._room_prefix}{room_key}"

    async def save_room(self, redis: Redis, map_and_meta: MapAndMeta) -> str:
        """Save room data to Redis

        Args:
            redis: Redis connection instance
            map_and_meta: Room map and metadata to save

        Returns:
            str: Generated room key

        Raises:
            RoomError: If saving fails
        """
        try:
            pk: int = await self._get_next_id(redis)
            room_key: str = make_room_key(pk)
            json_data = json.dumps(map_and_meta, cls=MapAndMetaEncoder)
            await redis.setex(self._make_key(room_key), settings.room_ttl, json_data)
            return room_key
        except (RedisError, TypeError, ValueError) as e:
            raise RoomError(f"Failed to save room: {e}") from e

    async def load_room(self, redis: Redis, room_key: str) -> MapAndMeta:
        """Load room data from Redis

        Args:
            redis: Redis connection instance
            room_key: Room key to load

        Returns:
            MapAndMeta: Room map and metadata

        Raises:
            RoomNotFoundError: If room is not found
            RoomSerializationError: If deserialization fails
        """
        try:
            raw_data: str = await redis.get(self._make_key(room_key))
            if not raw_data:
                raise RoomNotFoundError(f"Room {room_key} not found")

            data = json.loads(raw_data, object_hook=map_and_meta_deserializer)
            return cast(MapAndMeta, data)
        except json.JSONDecodeError as e:
            raise RoomSerializationError(f"Failed to deserialize room data: {e}") from e
        except RedisError as e:
            raise RoomError(f"Redis error while loading room: {e}") from e

    async def remove_room(self, redis: Redis, room_key: str) -> None:
        """Remove room data from Redis

        Args:
            redis: Redis connection instance
            room_key: Room key to remove

        Raises:
            RoomError: If removal fails
        """
        try:
            await redis.delete(self._make_key(room_key))
        except RedisError as e:
            raise RoomError(f"Failed to remove room: {e}") from e


room_repo = RoomRepo()
