class PlayerError(Exception):
    """Base exception for all player-related errors"""


class PlayerNotInit(PlayerError):
    """Player has not been properly initialized"""


class PlayerWrongAuthFlow(PlayerError):
    """Authentication flow violation"""


class PlayerTokenIsNotValid(PlayerError):
    """Invalid authentication token. Token has expired or been revoked"""
