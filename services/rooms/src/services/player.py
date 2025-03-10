import asyncio
import json
from abc import ABC, abstractmethod
from itertools import product
from typing import Callable, Coroutine, Iterable

from bitarray import bitarray
from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from app_types.common import PlayerStatus
from app_types.map import GameMap, Point
from app_types.messages import InMessage, OutMessage
from app_types.out_messages import AuthConfirmMessage
from exceptions.player import PlayerNotInit, PlayerTokenIsNotValid, PlayerWrongAuthFlow
from logger import get_logger
from metrics import WS_MESSAGE_SIZE
from services.auth import validate_token

logger = get_logger(__name__)


OnMassageType = Callable[["Player", InMessage], Coroutine[None, None, None]]
OnDisconnectType = Callable[["Player"], Coroutine[None, None, None]]


class MapCoordinator:
    def __init__(self, map_width: int, map_height: int):
        self._map_width = map_width
        self._map_height = map_height
        self._array_size = map_width * map_height

    def point_to_index(self, point: Point) -> int:
        return point.row * self._map_width + point.col

    def index_to_point(self, index: int) -> Point:
        return Point(index // self._map_width, index % self._map_width)

    def is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < self._map_height and 0 <= col < self._map_width


class Territory:
    def __init__(self, map_width: int, map_height: int):
        self._coord = MapCoordinator(map_width, map_height)
        self._territory_mask = bitarray(self._coord._array_size)
        self._territory_mask.setall(0)

    def add_point(self, point: Point) -> None:
        self._territory_mask[self._coord.point_to_index(point)] = 1

    def remove_point(self, point: Point) -> None:
        self._territory_mask[self._coord.point_to_index(point)] = 0

    def merge(self, other: "Territory") -> None:
        self._territory_mask |= other._territory_mask

    def contains(self, point: Point) -> bool:
        return bool(self._territory_mask[self._coord.point_to_index(point)])

    def clear(self) -> None:
        self._territory_mask.setall(0)

    def count(self) -> int:
        return self._territory_mask.count()

    def points(self) -> tuple[Point, ...]:
        return tuple(
            self._coord.index_to_point(i) for i in self._territory_mask.search(bitarray("1"))
        )


class Visibility:
    DIRECTIONS = tuple(product([-1, 0, 1], repeat=2))

    def __init__(self, map_width: int, map_height: int):
        self._coord = MapCoordinator(map_width, map_height)
        self._visible_mask = bitarray(self._coord._array_size)
        self._new_visible_mask = bitarray(self._coord._array_size)
        self._visible_mask.setall(0)
        self._new_visible_mask.setall(0)

    def update(self, territory_points: Iterable[Point]) -> tuple[Point, ...]:
        self._new_visible_mask.setall(0)

        for point in territory_points:
            for dr, dc in self.DIRECTIONS:
                new_row, new_col = point.row + dr, point.col + dc
                if self._coord.is_valid_position(new_row, new_col):
                    index = self._coord.point_to_index(Point(new_row, new_col))
                    self._new_visible_mask[index] = 1

        diff_mask = self._new_visible_mask ^ self._visible_mask
        diff_points = tuple(
            self._coord.index_to_point(i) for i in range(self._coord._array_size) if diff_mask[i]
        )

        self._visible_mask = self._new_visible_mask.copy()
        return diff_points

    def visible_points(self) -> tuple[Point, ...]:
        return tuple(
            self._coord.index_to_point(i) for i in self._visible_mask.search(bitarray("1"))
        )


class Player(ABC):
    def __init__(self, id: int, nick: str, map_size: tuple[int, int]):
        self.id: int = id
        self.nick: str = nick
        self._status: PlayerStatus = PlayerStatus.NOT_READY
        self._init_point: Point | None = None
        self._color: int | None = None

        map_height, map_width = map_size
        self.territory = Territory(map_width, map_height)
        self.visibility = Visibility(map_width, map_height)
        self.moves: asyncio.Queue[tuple[Point, Point]] = asyncio.Queue()

        self.receive_loop: asyncio.Task | None = None
        self._message_handler: OnMassageType | None = None
        self._disconnect_handler: OnDisconnectType | None = None
        self.cursor: Point | None = None
        self.prev_cursor: Point | None = None
        self.pov: GameMap = self._generate_empty_map(map_width, map_height)

    def _generate_empty_map(self, width: int, height: int) -> GameMap:
        return [[{} for _ in range(width)] for _ in range(height)]

    @property
    def color(self) -> int:
        if self._color is None:
            raise PlayerNotInit("Need set color")
        return self._color

    @color.setter
    def color(self, new_color: int):
        self._color = new_color

    @property
    def init_point(self) -> Point:
        if not self._init_point:
            raise PlayerNotInit("Need set init point")
        return self._init_point

    def set_init_point(self, init_point: Point) -> None:
        self._init_point = init_point
        self.territory.add_point(init_point)

    @property
    def hold(self) -> tuple[Point, ...]:
        return self.territory.points()

    @property
    def visible_points(self) -> tuple[Point, ...]:
        return self.visibility.visible_points()

    def update_visible_cells(self) -> tuple[Point, ...]:
        return self.visibility.update(self.hold)

    async def move(self, prev: Point | None, current: Point | None) -> None:
        if prev and current:
            await self.moves.put((prev, current))
            return
        self.reset_moves()

    def get_move_points(self) -> tuple[Point, Point] | None:
        try:
            return self.moves.get_nowait()
        except asyncio.QueueEmpty:
            return None

    def reset_moves(self) -> None:
        self.moves = asyncio.Queue()
        self.cursor = None
        self.prev_cursor = None

    @property
    def status(self) -> PlayerStatus:
        return self._status

    def set_lose(self) -> None:
        self._status = PlayerStatus.LOSER
        self.territory.clear()

    def set_win(self) -> None:
        self._status = PlayerStatus.WINNER

    def set_ready(self) -> None:
        self._status = PlayerStatus.READY

    def set_stop(self) -> None:
        self._status = PlayerStatus.STOPPED

    async def _receive_loop(self) -> None:
        while self._status != PlayerStatus.STOPPED:
            try:
                message = await asyncio.wait_for(self.receive_json(), 1)
                if self._message_handler:
                    await self._message_handler(self, message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error("Message handling error", exc_info=e)
                if self._disconnect_handler:
                    await self._disconnect_handler(self)
                break

    def set_message_handler(self, handler: OnMassageType) -> None:
        self._message_handler = handler

    def set_disconnect_handler(self, handler: OnDisconnectType) -> None:
        self._disconnect_handler = handler

    def start_listening(self) -> None:
        self.receive_loop = asyncio.create_task(self._receive_loop())

    async def stop_listening(self) -> None:
        self.set_stop()
        if self.receive_loop and not self.receive_loop.done():
            await self.receive_loop

    async def wait_messages(self):
        if self.receive_loop and not self.receive_loop.done():
            await self.receive_loop

    @property
    def power(self) -> int:
        return sum(self.pov[p.row][p.col].get("power", 0) for p in self.hold)

    def takeover_kingdom(self, other: "Player") -> None:
        self.territory.merge(other.territory)
        other.territory.clear()
        other.set_lose()

    @property
    def is_ready(self) -> bool:
        return self._status == PlayerStatus.READY

    @abstractmethod
    async def authenticate(self) -> bool:
        pass

    @abstractmethod
    async def receive_json(self) -> InMessage:
        pass

    @abstractmethod
    async def send_json(self, message: OutMessage) -> None:
        pass

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return NotImplemented
        return self.id == other.id


class WebsocketPlayer(Player):
    def __init__(self, id: int, nick: str, map_size: tuple[int, int], websocket: WebSocket):
        super().__init__(id, nick, map_size)
        self.websocket: WebSocket = websocket

    async def authenticate(self) -> bool:
        message = await self.receive_json()
        if message["at"] != "auth":
            raise PlayerWrongAuthFlow()

        if not await validate_token(message["token"]):
            raise PlayerTokenIsNotValid()

        await self.send_json(AuthConfirmMessage(at="auth", status=True))
        return True

    async def receive_json(self) -> InMessage:
        return await self.websocket.receive_json()

    async def send_json(self, message: OutMessage) -> None:
        if self.websocket.client_state == WebSocketState.CONNECTED:
            text_message = json.dumps(message, separators=(",", ":"), ensure_ascii=False)
            WS_MESSAGE_SIZE.labels(direction="out", message_type=message["at"]).observe(
                len(text_message)
            )
            await self.websocket.send_text(text_message)

    def __repr__(self) -> str:
        return f"WebsocketPlayer(id={self.id}, nick={self.nick})"
