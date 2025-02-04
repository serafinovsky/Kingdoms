class RoomError(Exception):
    """Common room error"""


class RoomAlreadyExistsError(RoomError):
    """Room already exists error"""


class RoomNotFoundError(RoomError):
    """Room not found error"""


class RoomNotReadyError(RoomError):
    """Room is not ready to play"""


class RoomInGameError(RoomError):
    """Game's already started"""


class RoomNoSlots(RoomError):
    """No slots in room"""
