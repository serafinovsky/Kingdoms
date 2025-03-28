from typing import Optional

from redis.asyncio import Redis

from app_types.map import CellType, MapAndMeta
from exceptions.room import (
    RoomNotFoundError,
    RoomWrongReplica,
)
from logger import get_logger
from repositories.room import lobby_repo, room_repo, sharding_repo
from services.player import Player
from services.room.game_room import GameRoom
from settings import settings

logger = get_logger(__name__)


# TODO делает слишком много, зарефакторить
class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, "GameRoom"] = {}

    async def save_room(self, redis: Redis, map_and_meta: MapAndMeta) -> str:
        room_key = await room_repo.save_room(redis, map_and_meta)
        return room_key

    async def get_or_create_room(self, redis: Redis, room_key: str) -> "GameRoom":
        replica = await sharding_repo.get_room_replica(redis, room_key)
        if replica and replica != settings.replica_id:
            raise RoomWrongReplica()

        if room_key in self.rooms:
            return self.rooms[room_key]

        map_and_meta = await room_repo.load_room(redis, room_key)
        if not map_and_meta:
            raise RoomNotFoundError()

        game_map, meta = map_and_meta["map"], map_and_meta["meta"]
        game_room = GameRoom(room_key, game_map, meta)
        self.rooms[room_key] = game_room
        await sharding_repo.set_room_replica(redis, room_key)
        await lobby_repo.add_room(redis, len(meta["points_of_interest"][CellType.SPAWN]), room_key)
        return game_room

    async def play_with_room(self, redis: Redis, room: "GameRoom", player: "Player") -> None:
        await lobby_repo.add_players(redis, room.room_key)

        try:
            await room.wait_all_ready(player)
        except Exception as e:
            await lobby_repo.remove_player(redis, room.room_key)
            raise e
        else:
            await lobby_repo.remove_room(redis, room.room_key)

        await room.play(player)
        await room.after_play(player)

    async def cleanup(
        self, redis: Redis, room: Optional["GameRoom"], player: Optional["Player"]
    ) -> None:
        if room:
            try:
                await lobby_repo.remove_player(redis, room.room_key)
            except Exception as e:
                logger.error("Error while removing player from lobby", exc_info=e, stack_info=True)

        if player:
            try:
                await player.stop_listening()
            except Exception as e:
                logger.error("Error while stopping player listening", exc_info=e, stack_info=True)

        if player and room:
            await room.disconnect(player)

        if room and (not room.allow_reconnect() or len(room.players.values()) == 0):
            try:
                await room_repo.remove_room(redis, room.room_key)
                await sharding_repo.remove_room_replica(redis, room.room_key)
                await lobby_repo.remove_room(redis, room.room_key)
            except Exception as e:
                logger.error("Error while clearing redis", exc_info=e, stack_info=True)
                pass

            try:
                room.cleanup()
            except Exception as e:
                pass

            if room.room_key in self.rooms:
                del self.rooms[room.room_key]


room_manager = RoomManager()
