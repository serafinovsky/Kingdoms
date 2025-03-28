from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Optional

from app_types.common import PlayerStatus
from app_types.map import GameMap
from metrics import TURN_DURATION
from services.player import Player
from services.room.map_manager import MapManager
from services.room.territory_manager import TerritoryManager
from utils import measure_time


class GameLoopStrategy(ABC):
    """Интерфейс стратегии для игрового цикла"""

    def __init__(self) -> None:
        super().__init__()
        self._on_turn_done: Optional[Callable[[], Awaitable[None]]] = None
        self._on_game_done: Optional[Callable[[], Awaitable[None]]] = None

    @abstractmethod
    async def init_turn(self, turn_number: int) -> None:
        """Вызывается в начале каждого хода"""
        pass

    @abstractmethod
    def make_turn(self) -> None:
        """Вызывается для выполнения хода"""
        pass

    def is_game_done(self) -> bool:
        """Проверяет, завершена ли игра"""
        return False

    async def finish_turn(self) -> None:
        """Вызывается в конце каждого хода"""
        if self._on_turn_done:
            await self._on_turn_done()

    async def finish_game(self) -> None:
        """Вызывается при завершении игры"""
        if self._on_game_done:
            await self._on_game_done()

    def set_on_turn_done(self, callback: Callable[[], Awaitable[None]]) -> None:
        self._on_turn_done = callback

    def set_on_game_done(self, callback: Callable[[], Awaitable[None]]) -> None:
        self._on_game_done = callback


class ClassicGameStrategy(GameLoopStrategy):
    """Стратегия для классической версии игры"""

    def __init__(self, game_map: GameMap, players: dict[int, Player]):
        self._game_map = game_map
        self._players = players
        self._map_manager = MapManager(game_map, 0)
        self._territory_manager = TerritoryManager(game_map)

    async def init_turn(self, turn_number: int) -> None:
        self._map_manager.current_turn = turn_number

    def make_turn(self) -> None:
        with measure_time(TURN_DURATION, {"operation": "update_map"}):
            self._map_manager.update_map(self._players)

        with measure_time(TURN_DURATION, {"operation": "process_moves"}):
            for player in self._players.values():
                move_points = player.get_move_points()
                if move_points:
                    player.prev_cursor, player.cursor = move_points
                    self._map_manager.process_move(player, move_points)

        with measure_time(TURN_DURATION, {"operation": "update_hold"}):
            self._territory_manager.update_territories(
                self._players, self._map_manager.get_map_diff()
            )
            self._map_manager.check_cursor(self._players)
            self._map_manager.clear_map_diff()

        with measure_time(TURN_DURATION, {"operation": "update_pov"}):
            for player in self._players.values():
                self._update_pov(player)

    async def finish_turn(self) -> None:
        with measure_time(TURN_DURATION, {"operation": "finish_turn"}):
            await super().finish_turn()

    def is_game_done(self) -> bool:
        return sum(player.is_ready for player in self._players.values()) == 1

    def _update_pov(self, player: Player) -> None:
        if player._status == PlayerStatus.LOSER or self.is_game_done():
            player.pov = self._game_map
            return

        diff = player.update_visible_cells()
        for point in diff:
            r, c = point
            pov_cell = player.pov[r][c]
            if "type" in pov_cell:
                del pov_cell["type"]
            if "player" in pov_cell:
                del pov_cell["player"]
            if "power" in pov_cell:
                del pov_cell["power"]

        for point in player.visible_points:
            r, c = point
            map_cell = self._game_map[r][c]
            pov_cell = player.pov[r][c]
            cell_type = map_cell.get("type")
            if cell_type:
                pov_cell["type"] = cell_type
            if "player" in map_cell:
                pov_cell["player"] = map_cell["player"]
            if "power" in map_cell:
                pov_cell["power"] = map_cell["power"]
