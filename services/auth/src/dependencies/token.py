from typing import Annotated

from fastapi import Cookie, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

from dependencies.common import get_fingerprint
from dependencies.store import get_redis_client
from repositories.auth import blacklist_repo
from schemas.auth import AccessPayload, RefreshPayload
from services.auth import decode_access_token, decode_refresh_token
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


async def get_refresh_payload(
    refresh_token: Annotated[str, Cookie(alias=settings.refresh_token_cookie)],
    redis: Annotated[Redis, Depends(get_redis_client)],
    fingerprint: Annotated[str, Depends(get_fingerprint)],
) -> RefreshPayload:
    try:
        refresh_payload = decode_refresh_token(refresh_token, fingerprint=fingerprint)
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
