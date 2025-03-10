import json
import time
from typing import Any, TypeVar, cast

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app_types.map import MapAndMeta, Point
from app_types.room import LobbyRoom
from exceptions.room import RoomError, RoomNotFoundError
from settings import settings
from utils import make_room_key

JsonType = str | int | float | bool | None | dict[str, Any] | list[Any]
T = TypeVar("T")


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
            raise RoomError(f"Failed to deserialize room data: {e}") from e
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


class ShardingRepo:
    def __init__(self) -> None:
        self._shard_prefix: str = "__shard:rooms:"

    def _make_key(self, room_key: str) -> str:
        return f"{self._shard_prefix}{room_key}"

    async def get_room_replica(self, redis: Redis, room_key: str) -> str | None:
        """Get replica ID where room is located

        Args:
            redis: Redis connection instance
            room_key: Room identifier

        Returns:
            Optional[str]: Replica ID or None if not found

        Raises:
            RoomError: If Redis operation fails
        """
        replica_id = await redis.get(self._make_key(room_key))
        return replica_id

    async def set_room_replica(self, redis: Redis, room_key: str) -> None:
        """Set replica ID for room

        Args:
            redis: Redis connection instance
            room_key: Room identifier
            replica_id: Replica identifier
            ttl: Time to live in seconds

        Raises:
            RoomError: If Redis operation fails
        """
        await redis.setex(self._make_key(room_key), settings.room_ttl, settings.replica_id)

    async def remove_room_replica(self, redis: Redis, room_key: str) -> None:
        """Remove room's replica mapping

        Args:
            redis: Redis connection instance
            room_key: Room identifier

        Raises:
            RoomError: If Redis operation fails
        """
        await redis.delete(self._make_key(room_key))


class LobbyRepository:
    def __init__(self):
        self._lobby_key = "lobby:rooms"
        self._room_prefix = "lobby:room:"

    def _make_room_key(self, room_id: str) -> str:
        return f"{self._room_prefix}{room_id}"

    async def add_room(self, redis: Redis, max_players: int, room_key: str) -> None:
        """Add room to lobby with initial data"""
        room_data = {"name": room_key, "max_players": max_players, "current_players": 0}
        async with redis.pipeline(transaction=True) as pipe:
            await pipe.hset(self._make_room_key(room_key), mapping=room_data)
            await pipe.zadd(self._lobby_key, {room_key: time.time()})
            await pipe.execute()

    async def add_players(self, redis: Redis, room_id: str) -> None:
        await redis.hincrby(self._make_room_key(room_id), "current_players", 1)

    async def remove_player(self, redis: Redis, room_id: str) -> None:
        await redis.hincrby(self._make_room_key(room_id), "current_players", -1)

    async def get_rooms(
        self,
        redis: Redis,
        offset: int = 0,
        limit: int = 50,
    ) -> list[LobbyRoom]:
        room_ids = await redis.zrange(
            self._lobby_key, start=offset, end=offset + limit - 1, desc=True
        )

        rooms = []
        for room_id in room_ids:
            room_data = await redis.hgetall(self._make_room_key(room_id))
            if room_data:
                rooms.append(
                    LobbyRoom(
                        name=room_data["name"],
                        max_players=int(room_data["max_players"]),
                        current_players=int(room_data["current_players"]),
                    )
                )
        return rooms

    async def remove_room(self, redis: Redis, room_id: str) -> None:
        async with redis.pipeline(transaction=True) as pipe:
            await pipe.delete(self._make_room_key(room_id))
            await pipe.zrem(self._lobby_key, room_id)
            await pipe.execute()


lobby_repo = LobbyRepository()
sharding_repo = ShardingRepo()
room_repo = RoomRepo()
