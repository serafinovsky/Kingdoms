from typing import Literal, TypedDict

from app_types.in_messages import (
    AuthMessage,
    ColorMessage,
    MoveMessage,
    ReadyMessage,
)
from app_types.out_messages import AuthConfirmMessage, PlayersMessage, StartMessage, UpdateMessage


class ChatMessage(TypedDict):
    at: Literal["chat"]
    user_id: int
    message: str
    username: str
    timestamp: str


InMessage = AuthMessage | ReadyMessage | MoveMessage | ColorMessage | ChatMessage


OutMessage = PlayersMessage | AuthConfirmMessage | StartMessage | UpdateMessage | ChatMessage
