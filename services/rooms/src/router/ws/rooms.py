from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket
from redis.asyncio import Redis

from dependencies.store import get_redis_client
from exceptions.player import PlayerTokenIsNotValid, PlayerWrongAuthFlow
from exceptions.room import RoomInGameError, RoomNoSlots, RoomNotFoundError, RoomWrongReplica
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
    await websocket.accept()
    try:
        room = await room_manager.get_or_create_room(redis, room_key)
        player = WebsocketPlayer(user_id, username, room.dimension, websocket)
        await room_manager.play_with_room(redis, room, player)
    except RoomWrongReplica:
        logger.info("Wrong replica", extra={"room_key": room_key, "user_id": user_id})
        await websocket.close(code=1008, reason="Wrong replica")
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
        logger.error(
            "Unexpected error",
            extra={
                "room_key": room_key,
                "user_id": user_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "error_module": type(e).__module__,
            },
            exc_info=True,
            stack_info=True,
        )
        await websocket.close(code=4999, reason="Something wrong")
    finally:
        await room_manager.cleanup_room(redis, room, player)
