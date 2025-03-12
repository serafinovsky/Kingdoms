from collections import defaultdict

from app_types.map import GameMap, Point
from services.player import Player


class TerritoryManager:
    def __init__(self, game_map: GameMap):
        self._game_map = game_map

    def update_territories(
        self, players: dict[int, "Player"], map_diff: dict[Point, tuple[int | None, int | None]]
    ) -> None:
        territory_updates = defaultdict(list)
        territory_removals = defaultdict(list)

        for point, (old_player, new_player) in map_diff.items():
            if new_player:
                territory_updates[new_player].append(point)
            if old_player and point in players[old_player].hold:
                territory_removals[old_player].append(point)

        for player_id, points in territory_updates.items():
            players[player_id].territory.batch_add_points(points)

        for player_id, points in territory_removals.items():
            players[player_id].territory.batch_remove_points(points)

        for player in players.values():
            player.territory.apply_batch_updates()

        captured_kingdoms: list[tuple[int, "Player"]] = []
        for player in players.values():
            row, col = player.init_point
            current_king = self._game_map[row][col].get("player")

            if not current_king:
                raise ValueError("WrongGameState")

            if current_king != player.id:
                captured_kingdoms.append((current_king, player))

        for new_king_id, captured_player in captured_kingdoms:
            points_to_update = captured_player.hold
            for point in points_to_update:
                self._game_map[point.row][point.col]["player"] = new_king_id
            players[new_king_id].takeover_kingdom(captured_player)
