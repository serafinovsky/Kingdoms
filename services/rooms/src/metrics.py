from prometheus_client import Gauge, Histogram, Summary

TURN_DURATION = Histogram(
    "game_turn_duration_seconds", "Time spent processing game turn", ["operation"]
)

GAME_STATE = Gauge(
    "game_state", "Current game state (0-waiting, 1-in_progress, 2-finished)", ["room_id"]
)


WS_MESSAGE_SIZE = Histogram(
    "ws_message_size_bytes",
    "WebSocket message size in bytes",
    ["direction", "message_type"],  # in/out, update/move/chat
    buckets=[64, 128, 256, 512, 1024, 2048, 4096],
)


GAME_DURATION = Summary("game_duration_turns_total", "Number of turns the game lasted")

# Territory metrics
TERRITORY_SIZE = Histogram(
    "player_territory_size_total",
    "Number of cells controlled by players at game end",
    buckets=[1, 5, 10, 25, 50, 100, 200, 500, 1000],
)
