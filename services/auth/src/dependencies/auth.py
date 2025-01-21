from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

from dependencies.store import get_redis_client
from repositories.auth import blacklist_repo
from schemas.auth import AccessPayload, RefreshPayload
from services.auth import (
    decode_access_token,
    decode_refresh_token,
    make_fingerprint,
)
from settings import settings

security = HTTPBearer()


async def get_access_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> AccessPayload:
    try:
        access_payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return access_payload


def get_fingerprint(request: Request):
    ua = request.headers.get("user-agent")
    return make_fingerprint(ua)


async def get_refresh_payload(
    refresh_token: Annotated[str, Cookie(alias=settings.refresh_token_cookie)],
    redis: Annotated[Redis, Depends(get_redis_client)],
    fingerprint: Annotated[str, Depends(get_fingerprint)],
) -> RefreshPayload:
    try:
        refresh_payload = decode_refresh_token(
            refresh_token, fingerprint=fingerprint
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if await blacklist_repo.is_blacklisted(redis, refresh_payload.jti):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return refresh_payload


async def get_client_ip(request: Request) -> str:
    """
    Extract the client's IP address from the request.

    Args:
        request (Request): The incoming request object.

    Returns:
        str: The client's IP address.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0]
    else:
        client_ip = request.client.host  # Fallback to the direct client IP

    return client_ip
