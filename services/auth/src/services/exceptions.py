class TokenError(Exception):
    pass


class DecodeError(TokenError):
    pass


class TokenExpiredError(DecodeError):
    pass
