import asyncio
from abc import ABC, abstractmethod
from itertools import product
from typing import Callable, Coroutine

from fastapi import WebSocket
from fastapi.websockets import WebSocketState

from app_types.common import PlayerStatus
from app_types.map import GameMap, Point
from app_types.messages import InMessage, OutMessage
from app_types.out_messages import AuthConfirmMessage
from exceptions.player import PlayerNotInit, PlayerTokenIsNotValid, PlayerWrongAuthFlow
from logger import get_logger
from services.auth import validate_token

logger = get_logger(__name__)


OnMassageType = Callable[["Player", InMessage], Coroutine[None, None, None]]
OnDisconnectType = Callable[["Player"], Coroutine[None, None, None]]


class Player(ABC):
    def __init__(self, id: int, nick: str):
        self.id: int = id
        self.nick: str = nick
        self.moves: asyncio.Queue[tuple[Point, Point]] = asyncio.Queue()
        self.receive_loop: asyncio.Task | None = None
        self._status: PlayerStatus = PlayerStatus.NOT_READY
        self._init_point: Point | None = None
        self.hold: set[Point] = set()
        self.visible_points: set[Point] = set()
        self._pov: GameMap | None = None
        self._message_handler: OnMassageType | None = None
        self._disconnect_handler: OnDisconnectType | None = None
        self._color: int | None = None

    @property
    def pov(self) -> GameMap:
        if self._pov is None:
            raise PlayerNotInit("Need set color")
        return self._pov

    @pov.setter
    def pov(self, pov: GameMap):
        self._pov = pov

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
        self.hold.add(init_point)

    async def _receive_loop(self) -> None:
        while self._status != PlayerStatus.STOPPED:
            try:
                message = await asyncio.wait_for(self.receive_json(), 1)
                if self._message_handler:
                    await self._message_handler(self, message)
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                logger.error("Something wrong", exc_info=e)
                if not self._disconnect_handler:
                    raise e
                await self._disconnect_handler(self)
                break

    @abstractmethod
    async def authenticate(self) -> bool:
        pass

    @abstractmethod
    async def receive_json(self) -> InMessage:
        pass

    @abstractmethod
    async def send_json(self, message: OutMessage) -> None:
        pass

    def set_message_handler(self, handler: OnMassageType) -> None:
        self._message_handler = handler

    def set_disconnect_handler(self, handler: OnDisconnectType) -> None:
        self._disconnect_handler = handler

    def start_listening(self) -> None:
        self.receive_loop = asyncio.create_task(self._receive_loop())

    async def wait_messages(self):
        if self.receive_loop and not self.receive_loop.done():
            await self.receive_loop

    async def stop_listening(self) -> None:
        self.set_stop()
        await self.wait_messages()

    def set_lose(self) -> None:
        self._status = PlayerStatus.LOSER
        self.hold.clear()

    def set_win(self) -> None:
        self._status = PlayerStatus.WINNER

    def set_ready(self) -> None:
        self._status = PlayerStatus.READY

    @property
    def power(self) -> int:
        return sum(self.pov[p.row][p.col].get("power", 0) for p in self.hold)

    @property
    def status(self) -> PlayerStatus:
        return self._status

    @property
    def is_ready(self) -> bool:
        return self._status == PlayerStatus.READY

    def set_stop(self) -> None:
        self._status = PlayerStatus.STOPPED

    def update_visible_cells(self) -> set[Point]:
        new_visible = {
            Point(row + dr, col + dc)
            for row, col in self.hold
            for dr, dc in product([-1, 0, 1], repeat=2)
        }
        diff = new_visible ^ self.visible_points
        self.visible_points.clear()
        self.visible_points.update(new_visible)
        return diff

    def get_move_points(self) -> tuple[Point, Point] | None:
        try:
            return self.moves.get_nowait()
        except asyncio.QueueEmpty:
            return None

    async def move(self, prev: Point, current: Point) -> None:
        await self.moves.put((prev, current))

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WebsocketPlayer):
            return NotImplemented
        return self.id == other.id


class WebsocketPlayer(Player):
    def __init__(self, id: int, nick: str, websocket: WebSocket):
        super().__init__(id, nick)
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
            await self.websocket.send_json(message)

    def __repr__(self) -> str:
        return f"WebsocketPlayer(id={self.id}, nick={self.nick})"
