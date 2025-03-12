import asyncio
import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app_types.common import GameStatus
from app_types.map import CellType, Point
from app_types.messages import InMessage
from app_types.out_messages import GameStat, PlayerData, PlayersMessage, StartMessage, UpdateMessage
from exceptions.room import (
    RoomInGameError,
    RoomNoSlots,
    RoomNotReadyError,
)
from logger import get_logger
from metrics import TERRITORY_SIZE
from services.player import Player
from services.room.game_loop import GameLoop
from services.room.strategies import ClassicGameStrategy
from settings import settings

if TYPE_CHECKING:
    from services.room.game_room import GameRoom

logger = get_logger(__name__)


class GameState(ABC):
    def __init__(self, room: "GameRoom"):
        self._room = room

    @abstractmethod
    async def handle_player_message(self, player: "Player", message: InMessage) -> None:
        pass

    @abstractmethod
    async def connect(self, player: "Player") -> None:
        pass

    @abstractmethod
    async def play(self, player: "Player") -> None:
        pass

    def allow_reconnect(self) -> bool:
        return False

    @abstractmethod
    async def cleanup(self) -> None:
        pass

    @abstractmethod
    async def after_play(self, player: "Player") -> None:
        pass

    @abstractmethod
    async def disconnect(self, player: "Player") -> None:
        pass


class WaitingState(GameState):
    def __init__(self, room: "GameRoom"):
        super().__init__(room)
        self._lock: asyncio.Lock = asyncio.Lock()
        self._game_start_condition: asyncio.Condition = asyncio.Condition()
        self._colors: dict[int, Player | None] = {c: None for c in range(settings.colors_count)}

    def allow_reconnect(self) -> bool:
        return True

    async def handle_player_message(self, player: "Player", message: InMessage) -> None:
        match message["at"]:
            case "color":
                async with self._lock:
                    await self._release_color(player=player)
                    await self._take_color(player=player, color_pos=message["color"])
                await self._room.broadcast(self._players_message())
            case "ready":
                player.set_ready()
                await self._room.broadcast(self._players_message())
                await self._check_all_players_ready()

    async def connect(self, player: "Player") -> None:
        await player.authenticate()
        async with self._lock:
            await self._take_slot(player)
            await self._take_color(player)
            self._room.register_player(player)

        player.start_listening()
        await self._room.broadcast(self._players_message())

        async with self._game_start_condition:
            while not await self._is_all_ready():
                await self._game_start_condition.wait()

            if self._room.players:
                self._room.transition_to(GameStatus.IN_PROGRESS)

    async def cleanup(self) -> None:
        for player in self._room.players.values():
            await player.stop_listening()

    async def disconnect(self, player: "Player") -> None:
        async with self._lock:
            self._room.exclude_player(player)
            await self._release_color(player=player)
            await self._release_slot(player=player)

        await self._room.broadcast(self._players_message())
        await self._check_all_players_ready()

    async def play(self, player: "Player") -> None:
        raise RoomNotReadyError("You need to connect firstly")

    async def after_play(self, player: "Player") -> None:
        raise RoomNotReadyError("Wrong state")

    async def _get_slot(self) -> Point:
        if not self._room.slots:
            raise RoomNoSlots("There is not slots in the room")

        random.shuffle(self._room.slots)
        return self._room.slots.pop()

    async def _take_slot(self, player: "Player") -> None:
        slot = await self._get_slot()
        row, col = slot
        player.set_init_point(slot)
        init_point = self._room.game_map[row][col]
        init_point["type"] = CellType.KING
        init_point["player"] = player.id
        init_point["power"] = settings.default_king_power

    async def _release_slot(self, player: "Player") -> None:
        self._room.slots.append(player.init_point)
        row, col = player.init_point
        init_point = self._room.game_map[row][col]
        init_point["type"] = CellType.SPAWN
        if "player" in init_point:
            del init_point["player"]
        if "power" in init_point:
            del init_point["power"]

    def _get_first_empty_color_id(self) -> int | None:
        for c_id, color_player in self._colors.items():
            if not color_player:
                return c_id

    async def _take_color(self, player: Player, color_pos: int | None = None) -> None:
        color_pos = color_pos or self._get_first_empty_color_id()
        if color_pos is None:
            return

        if not self._colors[color_pos]:
            self._colors[color_pos] = player
            player.color = color_pos

    async def _release_color(self, player: "Player") -> None:
        if self._colors[player.color] is not None and self._colors[player.color] is player:
            self._colors[player.color] = None

    def _players_message(self) -> PlayersMessage:
        players = [
            PlayerData(id=p.id, username=p.nick, color=p.color, status=p.status)
            for p in self._room.players.values()
        ]
        return PlayersMessage(at="players", players=players)

    async def _is_all_ready(self) -> bool:
        async with self._lock:
            all_ready = all(player.is_ready for player in self._room.players.values())
            return len(self._room.players) > 1 and all_ready

    async def _check_all_players_ready(self) -> None:
        async with self._game_start_condition:
            if await self._is_all_ready():
                self._game_start_condition.notify_all()


class GameInProgressState(GameState):
    def __init__(self, room: "GameRoom"):
        super().__init__(room)
        self._game_strategy = ClassicGameStrategy(room.game_map, room.players)
        self._game_strategy.set_on_turn_done(self._broadcast_state)
        self._game_strategy.set_on_game_done(self._next_state)
        self._game_loop = GameLoop(
            self._game_strategy,
        )

    async def cleanup(self) -> None:
        await self._game_loop.stop()
        for player in self._room.players.values():
            await player.stop_listening()

    async def connect(self, player: "Player") -> None:
        raise RoomInGameError("Game's already started")

    async def disconnect(self, player: "Player") -> None:
        self._room.exclude_player(player)

    async def handle_player_message(self, player: "Player", message: InMessage) -> None:
        match message["at"]:
            case "move":
                previous = Point(**message.get("previous")) if message.get("previous") else None
                current = Point(**message.get("current")) if message.get("current") else None
                await player.move(previous, current)

    async def play(self, player: "Player") -> None:
        await self._room.broadcast(StartMessage(at="start"))
        await self._game_loop.start()
        try:
            await self._game_loop.wait()
        except Exception as e:
            logger.error(e, exc_info=e, stack_info=True)
            raise e

    async def after_play(self, player: "Player") -> None:
        raise RoomNotReadyError("Wrong state")

    def _update_message(self, player: "Player") -> UpdateMessage:
        TERRITORY_SIZE.observe(player.territory.count())
        message = UpdateMessage(
            at="update",
            map=player.pov,
            turn=self._game_loop.current_turn,
            stat=(
                PlayerData(
                    id=player.id, username=player.nick, color=player.color, status=player.status
                ),
                GameStat(fields=player.territory.count(), power=player.power),
            ),
        )
        if player.cursor:
            message["cursor"] = {"row": player.cursor.row, "col": player.cursor.col}
        if player.prev_cursor:
            message["prev_cursor"] = {"row": player.prev_cursor.row, "col": player.prev_cursor.col}
        return message

    async def _broadcast_state(self) -> None:
        await self._room.broadcast(self._update_message)

    async def _next_state(self) -> None:
        self._room.transition_to(GameStatus.FINISHED)


class GameFinished(GameState):
    async def handle_player_message(self, player: "Player", message: InMessage) -> None:
        pass

    async def cleanup(self) -> None:
        for player in self._room.players.values():
            await player.stop_listening()

    async def connect(self, player: "Player") -> None:
        raise RoomNotReadyError("Wrong state")

    async def play(self, player: "Player") -> None:
        raise RoomNotReadyError("Wrong state")

    async def after_play(self, player: "Player") -> None:
        await player.wait_messages()

    async def disconnect(self, player: "Player") -> None:
        self._room.exclude_player(player)
