import hashlib
from functools import partial
from typing import Callable, Type, TypeVar

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel, ValidationError

from logger import logging
from schemas.auth import (
    AccessPayload,
    RefreshPayload,
)
from services.exceptions import DecodeError, TokenError, TokenExpiredError
from settings import settings

logger = logging.getLogger(__name__)


PayloadSchema = dict[str, str | int]
T = TypeVar("T", bound=BaseModel)


class RefreshTokenCookie(BaseModel):
    value: str
    key: str = settings.refresh_token_cookie
    httponly: bool = True
    secure: bool = True
    samesite: str = "strict"
    path: str = "/api/v1/auth/"
    max_age: int = settings.refresh_token_ttl


class AccessToken(BaseModel):
    access_token: str


def create_token(payload: PayloadSchema, secret: str) -> str:
    """
    Create a JWT token with the given payload and secret.

    Args:
        payload (PayloadSchema): Dictionary containing token payload
        secret (str): Secret key for token signing

    Returns:
        str: Encoded JWT token

    Raises:
        TokenError: If token creation fails
    """
    try:
        return jwt.encode(payload, secret, algorithm="HS256")
    except Exception as e:
        logger.error(f"Token creation failed: {str(e)}")
        raise TokenError("Unexpected error while encode token")


def decode_token(token: str, secret: str, model: Type[T]) -> T:
    """
    Decode and validate a JWT token.

    Args:
        token (str): JWT token to decode
        secret (str): Secret key for token validation
        model (Type[T]): Pydantic model for payload validation

    Returns:
        T: Validated payload model instance

    Raises:
        TokenExpiredError: If token has expired
        DecodeError: If token is invalid or validation fails
    """
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except ExpiredSignatureError as e:
        logger.warning(f"Token expired: {str(e)}")
        raise TokenExpiredError()
    except InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise DecodeError("Bad token")

    try:
        return model(**payload)
    except ValidationError as e:
        logger.error(f"Payload validation failed: {str(e)}", exc_info=e)
        raise DecodeError("Unexpected schema")


def decode_refresh_token(token: str, fingerprint: str) -> RefreshPayload:
    """
    Decode and validate a refresh token with fingerprint check.

    Args:
        token (str): Refresh token to decode
        fingerprint (str): Fingerprint to validate against

    Returns:
        RefreshPayload: Validated refresh token payload

    Raises:
        DecodeError: If token is invalid or fingerprint doesn't match
    """
    refresh_token = decode_token(token, settings.refresh_jwt_secret, RefreshPayload)

    if refresh_token.fgp != fingerprint:
        logger.warning("Fingerprint mismatch detected")
        raise DecodeError("Fingerprint mismatch detected")

    return refresh_token


def make_fingerprint(*args: str) -> str:
    """
    Generate a secure fingerprint from provided arguments.

    Args:
        *args: Variable length string arguments to include in fingerprint

    Returns:
        str: SHA-256 hash of concatenated arguments
    """
    try:
        args_string = "|".join(map(str, args))
        return hashlib.sha256(args_string.encode()).hexdigest()
    except Exception as e:
        logger.error(f"Fingerprint generation failed: {str(e)}")
        raise


def token_response(
    refresh_payload: RefreshPayload,
    access_payload: AccessPayload,
) -> tuple[RefreshTokenCookie, AccessToken]:
    """
    Generate secure access and refresh tokens with proper configurations.

    Args:
        refresh_payload: Payload for refresh token
        access_payload: Payload for access token

    Returns:
        tuple: (RefreshTokenCookie, AccessToken)

    Raises:
        TokenError: If token generation fails
    """
    try:
        rt = create_token(refresh_payload.model_dump(), settings.refresh_jwt_secret)
        at = create_token(access_payload.model_dump(), settings.access_jwt_secret)
    except Exception as e:
        logger.error(f"Token response generation failed: {str(e)}")
        raise TokenError("Can't create tokens")

    return RefreshTokenCookie(value=rt), AccessToken(access_token=at)


decode_access_token: Callable[[str], AccessPayload] = partial(
    decode_token, secret=settings.access_jwt_secret, model=AccessPayload
)
