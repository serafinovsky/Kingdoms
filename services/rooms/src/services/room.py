import asyncio
import random
import time
from abc import ABC, abstractmethod
from itertools import chain
from typing import Callable

from redis.asyncio import Redis

from app_types.common import GameStatus, PlayerStatus
from app_types.map import Cell, CellType, GameMap, MapAndMeta, MapMeta, Point
from app_types.messages import InMessage, OutMessage
from app_types.out_messages import GameStat, PlayerData, PlayersMessage, StartMessage, UpdateMessage
from exceptions.room import RoomInGameError, RoomNoSlots, RoomNotFoundError, RoomNotReadyError
from logger import get_logger
from repositories.room import room_repo
from services.player import Player
from settings import settings

logger = get_logger(__name__)


class RoomManager:
    def __init__(self) -> None:
        self.rooms: dict[str, "GameRoom"] = {}
        self.lock = asyncio.Lock()

    async def init_room(self, redis: Redis, map_and_meta: MapAndMeta) -> str:
        room_key = await room_repo.save_room(redis, map_and_meta)
        return room_key

    async def get_or_create_room(self, redis: Redis, room_key: str) -> "GameRoom":
        async with self.lock:
            if room_key in self.rooms:
                return self.rooms[room_key]

            map_and_meta = await room_repo.load_room(redis, room_key)
            if not map_and_meta:
                raise RoomNotFoundError()
            game_map, meta = map_and_meta["map"], map_and_meta["meta"]
            game_room = GameRoom(room_key, game_map, meta)
            self.rooms[room_key] = game_room
            return game_room

    async def cleanup_room(self, redis: Redis, room_key: str) -> None:
        await room_repo.remove_room(redis, room_key)
        if room_key in self.rooms:
            del self.rooms[room_key]


room_manager = RoomManager()


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

    def need_cleanup(self) -> bool:
        return True

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

    def need_cleanup(self) -> bool:
        return False

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
            await self._game_start_condition.wait()
            if self._room.players:
                self._room.transition_to(GameStatus.IN_PROGRESS)

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
        if self._colors[player.color] is not None:
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
            return len(self._room.players) == 0 or len(self._room.players) > 1 and all_ready

    async def _check_all_players_ready(self) -> None:
        async with self._game_start_condition:
            if await self._is_all_ready():
                self._game_start_condition.notify_all()


class GameInProgressState(GameState):
    def __init__(self, room: "GameRoom"):
        super().__init__(room)
        self._game_loop_task: asyncio.Task = asyncio.create_task(self._game_loop())
        self._map_diff: dict[Point, tuple[int | None, int | None]] = {}
        self._current_turn: int = 0
        self._lock: asyncio.Lock = asyncio.Lock()
        self._start_loop: asyncio.Event = asyncio.Event()

    async def connect(self, player: "Player") -> None:
        raise RoomInGameError("Game's already started")

    async def disconnect(self, player: "Player") -> None:
        async with self._lock:
            self._room.exclude_player(player)

    async def handle_player_message(self, player: "Player", message: InMessage) -> None:
        match message["at"]:
            case "move":
                await player.move(Point(**message["previous"]), Point(**message["current"]))

    async def play(self, player: "Player") -> None:
        await self._room.broadcast(StartMessage(at="start"))
        player.pov = [[{"type": CellType.HIDE} for _ in row] for row in self._room.game_map]
        self._start_loop.set()
        try:
            await self._game_loop_task
        except Exception as e:
            logger.error(e, exc_info=e, stack_info=True)
            raise e

        self._room.transition_to(GameStatus.FINISHED)

    async def after_play(self, player: "Player") -> None:
        raise RoomNotReadyError("Wrong state")

    async def _game_loop(self) -> None:
        await self._start_loop.wait()

        while not self._is_game_done():
            self._current_turn += 1
            start = time.perf_counter()
            self._make_turn()
            await self._room.broadcast(self._update_message)
            elapsed = time.perf_counter() - start
            await asyncio.sleep(max(0.7 - elapsed, 0))
        self._make_turn()
        await self._room.broadcast(self._update_message)

    def _is_game_done(self):
        return sum(player.is_ready for player in self._room.players.values()) == 1

    def _make_turn(self):
        self._update_map()
        for player in self._room.players.values():
            self._process_player_move(player)
        self._update_players_hold()

        for player in self._room.players.values():
            self._update_pov(player)

    def _process_player_move(self, player: "Player") -> None:
        move_points = player.get_move_points()
        if not move_points:
            return

        cursor, next_move = move_points
        r, c = cursor
        new_r, new_c = next_move
        if not self._is_valid_position(new_r, new_c):
            return

        target_cell: Cell = self._room.game_map[new_r][new_c]
        target_cell_type = target_cell["type"]
        target_cell_power = target_cell.get("power", 0)
        target_cell_player = target_cell.get("player")
        if target_cell_type == CellType.BLOCKER:
            return

        current_cell: Cell = self._room.game_map[r][c]
        current_cell_power = current_cell.get("power", 0)
        current_cell_player = current_cell.get("player", 0) - 1  # при переходе в клетке остается 1
        if not current_cell_player or current_cell_player != player.id or current_cell_power <= 1:
            return

        if current_cell_player == target_cell_player:
            current_cell["power"] = 1
            target_cell["power"] = target_cell_power + current_cell_power
            return

        power_diff = current_cell_power - target_cell_power
        if power_diff < 0:
            current_cell["power"] = 1
            target_cell["power"] = abs(power_diff)
            return

        target_cell["player"] = current_cell_player
        target_cell["power"] = power_diff
        current_cell["power"] = 1
        self._map_diff[next_move] = (target_cell_player, current_cell_player)

    def _update_players_hold(self) -> None:
        for point, (old_player, new_player) in self._map_diff.items():
            r, c = point
            if new_player:
                self._room.players[new_player].hold.add(point)
            if old_player and point in self._room.players[old_player].hold:
                self._room.players[old_player].hold.remove(point)
        self._map_diff.clear()

        for player in self._room.players.values():
            row, col = player.init_point
            fact_player = self._room.game_map[row][col].get("player")
            if not fact_player:
                raise ValueError("WrongGameState")  # Своя ошика

            if fact_player != player.id:
                for point in player.hold:
                    r, c = point
                    self._room.game_map[r][c]["player"] = fact_player
                self._room.players[fact_player].hold |= player.hold
                player.set_lose()

    def _update_map(self) -> None:
        for point in chain.from_iterable(p.hold for p in self._room.players.values()):
            cell: Cell = self._room.game_map[point.row][point.col]
            if cell["type"] == CellType.KING:
                cell["power"] = cell.get("power", 0) + 1
            if cell["type"] == CellType.CASTLE and cell.get("player"):
                cell["power"] = cell.get("power", 0) + 1
            elif self._current_turn % 15 == 0:
                cell["power"] = cell.get("power", 0) + 1

    def _update_pov(self, player: "Player") -> None:
        if player._status == PlayerStatus.LOSER or self._is_game_done():
            player.pov = self._room.game_map
            return

        diff = player.update_visible_cells()
        for point in diff:
            r, c = point
            if not self._is_valid_position(r, c):
                continue

            pov_cell = player.pov[r][c]
            pov_cell["type"] = CellType.HIDE
            if "player" in pov_cell:
                del pov_cell["player"]
            if "power" in pov_cell:
                del pov_cell["power"]

        for point in player.visible_points:
            r, c = point
            if not self._is_valid_position(r, c):
                continue
            map_cell = self._room.game_map[r][c]
            pov_cell = player.pov[r][c]
            pov_cell["type"] = map_cell["type"]
            if "player" in map_cell:
                pov_cell["player"] = map_cell["player"]
            if "power" in map_cell:
                pov_cell["power"] = map_cell["power"]

    def _is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < len(self._room.game_map) and 0 <= col < len(self._room.game_map[0])

    def _update_message(self, player: "Player") -> UpdateMessage:
        return UpdateMessage(
            at="update",
            map=player.pov,
            turn=self._current_turn,
            stat=(
                PlayerData(
                    id=player.id, username=player.nick, color=player.color, status=player.status
                ),
                GameStat(fields=len(player.hold), power=player.power),
            ),
        )


class GameFinished(GameState):
    async def handle_player_message(self, player: "Player", message: InMessage) -> None:
        pass

    async def connect(self, player: "Player") -> None:
        raise RoomNotReadyError("Wrong state")

    async def play(self, player: "Player") -> None:
        raise RoomNotReadyError("Wrong state")

    async def after_play(self, player: "Player") -> None:
        await player.wait_messages()

    async def disconnect(self, player: "Player") -> None:
        self._room.exclude_player(player)


MessageType = OutMessage | Callable[["Player"], OutMessage]


class GameRoom:
    def __init__(self, room_key: str, game_map: GameMap, meta: MapMeta):
        self._states = {
            GameStatus.WAITING_FOR_PLAYERS: WaitingState(self),
            GameStatus.IN_PROGRESS: GameInProgressState(self),
            GameStatus.FINISHED: GameFinished(self),
        }
        self._state: GameState = self._states[GameStatus.WAITING_FOR_PLAYERS]
        self._room_key: str = room_key
        self.players: dict[int, "Player"] = {}
        self.game_map: GameMap = self.prepare_map(game_map)
        self.meta: MapMeta = meta
        self.slots: list[Point] = meta["points_of_interest"].get(CellType.SPAWN, [])

    def prepare_map(self, game_map: GameMap) -> GameMap:
        for row in game_map:
            for cell in row:
                if cell["type"] == CellType.CASTLE:
                    cell["power"] = settings.default_castle_power
        return game_map

    def transition_to(self, new_state: GameStatus) -> None:
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

    async def connect(self, player: "Player") -> None:
        await self._state.connect(player)

    async def disconnect(self, player: "Player") -> None:
        await self._state.disconnect(player)

    def need_cleanup(self) -> bool:
        return self._state.need_cleanup()

    async def play(self, player: "Player") -> None:
        await self._state.play(player)

    async def after_play(self, player: "Player") -> None:
        await self._state.after_play(player)

    async def handle_player_message(self, player: "Player", message: InMessage) -> None:
        match message["at"]:
            case "chat":
                await self.broadcast(message)
                return
        await self._state.handle_player_message(player, message)
