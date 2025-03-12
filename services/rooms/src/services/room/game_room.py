import asyncio
from typing import Callable

from app_types.common import GameStatus
from app_types.map import CellType, GameMap, MapMeta, Point
from app_types.messages import InMessage, OutMessage
from logger import get_logger
from metrics import GAME_STATE
from services.player import Player
from services.room.game_states import GameFinished, GameInProgressState, GameState, WaitingState
from settings import settings

logger = get_logger(__name__)

MessageType = OutMessage | Callable[["Player"], OutMessage]


class GameRoom:
    def __init__(self, room_key: str, game_map: GameMap, meta: MapMeta):
        self.game_map: GameMap = self.prepare_map(game_map)
        self.room_key: str = room_key
        self.players: dict[int, "Player"] = {}
        self.meta: MapMeta = meta
        self.slots: list[Point] = meta["points_of_interest"].get(CellType.SPAWN, [])
        self._states = {
            GameStatus.WAITING_FOR_PLAYERS: WaitingState(self),
            GameStatus.IN_PROGRESS: GameInProgressState(self),
            GameStatus.FINISHED: GameFinished(self),
        }
        self._state: GameState = self._states[GameStatus.WAITING_FOR_PLAYERS]
        GAME_STATE.labels(room_id=room_key).set(GameStatus.WAITING_FOR_PLAYERS.value)

    @property
    def dimension(self) -> tuple[int, int]:
        return len(self.game_map), len(self.game_map[0])

    def prepare_map(self, game_map: GameMap) -> GameMap:
        for row in game_map:
            for cell in row:
                if cell.get("type") == CellType.CASTLE:
                    cell["power"] = settings.default_castle_power
        return game_map

    def transition_to(self, new_state: GameStatus) -> None:
        GAME_STATE.labels(room_id=self.room_key).set(new_state.value)
        self._state = self._states[new_state]

    def register_player(self, player: "Player") -> None:
        self.players[player.id] = player
        player.set_message_handler(self.handle_player_message)
        player.set_disconnect_handler(self.disconnect)

    def exclude_player(self, player: "Player") -> None:
        if player.id in self.players:
            del self.players[player.id]

    async def broadcast(self, message: MessageType) -> None:
        tasks = [self.send_message(player, message) for player in self.players.values()]
        await asyncio.gather(*tasks)

    async def send_message(self, player: "Player", message: MessageType) -> None:
        try:
            message = message(player) if callable(message) else message
            await player.send_json(message)
        except Exception as e:
            logger.error("Error while sending", exc_info=e, stack_info=True)
            await self.disconnect(player)

    async def wait_all_ready(self, player: "Player") -> None:
        await self._state.connect(player)

    async def disconnect(self, player: "Player") -> None:
        await self._state.disconnect(player)

    def allow_reconnect(self) -> bool:
        return self._state.allow_reconnect()

    async def play(self, player: "Player") -> None:
        await self._state.play(player)

    async def after_play(self, player: "Player") -> None:
        await self._state.after_play(player)

    async def cleanup(self) -> None:
        await self._state.cleanup()

    async def handle_player_message(self, player: "Player", message: InMessage) -> None:
        match message["at"]:
            case "chat":
                await self.broadcast(message)
                return
        await self._state.handle_player_message(player, message)
