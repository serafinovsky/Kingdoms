from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket
from redis.asyncio import Redis

from dependencies.store import get_redis_client
from exceptions.player import PlayerTokenIsNotValid, PlayerWrongAuthFlow
from exceptions.room import RoomInGameError, RoomNoSlots, RoomNotFoundError
from logger import get_logger
from services.player import WebsocketPlayer
from services.room import room_manager

logger = get_logger(__name__)
rooms_router = APIRouter(prefix="/rooms", tags=["rooms"])


@rooms_router.websocket("/{room_key}/")
async def ws_room(
    websocket: WebSocket,
    room_key: str,
    user_id: int,
    username: str,
    redis: Annotated[Redis, Depends(get_redis_client)],
):
    room = player = None
    room = await room_manager.get_or_create_room(redis, room_key)
    await websocket.accept()
    try:
        player = WebsocketPlayer(user_id, username, websocket)
        await room.connect(player)
        await room.play(player)
        await room.after_play(player)
    except RoomNoSlots:
        await websocket.close(code=4010, reason="There is not slots")
    except RoomInGameError:
        await websocket.close(code=4020, reason="Room is in game")
    except PlayerTokenIsNotValid:
        await websocket.close(code=4030, reason="Auth error")
    except PlayerWrongAuthFlow:
        await websocket.close(code=4031, reason="Auth flow error")
    except RoomNotFoundError:
        await websocket.close(code=4040, reason="Room not found")
    except Exception as e:
        logger.error("Something wrong", exc_info=e, stack_info=True)
        await websocket.close(code=4100, reason="Something wrong")
    finally:
        if player:
            await room.disconnect(player)
            await player.stop_listening()
        if room.need_cleanup() and len(room.players.values()) == 0:
            await room_manager.cleanup_room(redis, room_key)
