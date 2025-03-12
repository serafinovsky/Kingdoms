from itertools import chain

from app_types.map import Cell, CellType, GameMap, Point
from services.player import Player


class MapManager:
    def __init__(self, game_map: GameMap, current_turn: int):
        self._game_map = game_map
        self.current_turn = current_turn
        self._map_diff: dict[Point, tuple[int | None, int | None]] = {}

    def update_map(self, players: dict[int, "Player"]) -> None:
        for point in chain.from_iterable(p.hold for p in players.values()):
            cell: Cell = self._game_map[point.row][point.col]
            cell_type = cell.get("type")
            if cell_type == CellType.KING:
                cell["power"] = cell.get("power", 0) + 1
            if cell_type == CellType.CASTLE and cell.get("player"):
                cell["power"] = cell.get("power", 0) + 1
            elif self.current_turn % 15 == 0:
                cell["power"] = cell.get("power", 0) + 1

    def process_move(self, player: "Player", move_points: tuple[Point, Point]) -> None:
        if not move_points:
            return

        cursor, next_move = move_points
        r, c = cursor
        new_r, new_c = next_move
        if not self._is_valid_position(new_r, new_c):
            player.reset_moves()
            return

        target_cell: Cell = self._game_map[new_r][new_c]
        target_cell_type = target_cell.get("type", None)
        target_cell_power = target_cell.get("power", 0)
        target_cell_player = target_cell.get("player")
        if target_cell_type == CellType.BLOCKER:
            player.reset_moves()
            return

        current_cell: Cell = self._game_map[r][c]
        current_cell_power = current_cell.get("power", 0) - 1  # при переходе в клетке остается 1
        current_cell_player = current_cell.get("player")
        if not current_cell_player or current_cell_player != player.id or current_cell_power < 1:
            player.reset_moves()
            return

        if current_cell_player == target_cell_player:
            current_cell["power"] = 1
            target_cell["power"] = target_cell_power + current_cell_power
            return

        power_diff = current_cell_power - target_cell_power
        if power_diff < 0:
            current_cell["power"] = 1
            target_cell["power"] = abs(power_diff)
            player.reset_moves()
            return

        target_cell["player"] = current_cell_player
        target_cell["power"] = power_diff
        current_cell["power"] = 1
        self._map_diff[next_move] = (target_cell_player, current_cell_player)

    def get_map_diff(self) -> dict[Point, tuple[int | None, int | None]]:
        return self._map_diff

    def clear_map_diff(self) -> None:
        self._map_diff.clear()

    def check_cursor(self, players: dict[int, "Player"]) -> None:
        for player in players.values():
            if player.cursor and not player.territory.contains(player.cursor):
                player.reset_moves()

    def _is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < len(self._game_map) and 0 <= col < len(self._game_map[0])
