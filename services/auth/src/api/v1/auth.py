from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from fastapi.responses import ORJSONResponse, RedirectResponse
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app_types.common import Provider
from auth_flow import AuthError, get_auth_flow
from dependencies.auth import (
    get_access_payload,
    get_client_ip,
    get_fingerprint,
    get_refresh_payload,
)
from dependencies.store import get_pg_autocommit_session, get_redis_client
from logger import logging
from repositories.auth import blacklist_repo, login_repo, user_repo
from repositories.user import profile_repo
from schemas.auth import (
    AccessPayload,
    AuthorizeData,
    LoginInfo,
    RefreshPayload,
)
from services.auth import (
    AccessToken,
    get_or_create_user,
    new_login,
    token_response,
)
from settings import settings

auth_router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@auth_router.get(
    "/{provider}/authorize/",
    summary="Initiate OAuth authorization flow",
    response_class=RedirectResponse,
)
async def authorize(provider: Provider) -> RedirectResponse:
    return get_auth_flow(provider).authorize_url()


@auth_router.post(
    "/{provider}/token/",
    summary="Exchange authorization code for tokens",
    response_model=AccessToken,
)
async def token(
    response: Response,
    provider: Provider,
    auth_data: AuthorizeData,
    user_agent: Annotated[str, Header(alias="user-agent")],
    ip: Annotated[str, Depends(get_client_ip)],
    fingerprint: Annotated[str, Depends(get_fingerprint)],
    db: Annotated[AsyncSession, Depends(get_pg_autocommit_session)],
) -> AccessToken:
    try:
        flow = get_auth_flow(provider)
        user_data = await flow.process_response(auth_data.code)
    except AuthError as e:
        logger.exception(
            f"Authentication error: {str(e)}", stack_info=True, exc_info=e
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
    except Exception as e:
        logger.exception(
            f"Unexpected error during authentication: {str(e)}",
            stack_info=True,
            exc_info=e,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    user = await get_or_create_user(
        db=db,
        user_repo=user_repo,
        profile_repo=profile_repo,
        user_data=user_data,
    )
    await new_login(
        db=db,
        login_repo=login_repo,
        info=LoginInfo(
            user_id=user.id,
            provider=provider,
            user_agent=user_agent,
            ip_address=ip,
        ),
    )

    refresh_payload = RefreshPayload(sub=user.id, fgp=fingerprint)
    access_payload = AccessPayload(sub=user.id)
    rt, at = token_response(refresh_payload, access_payload)
    response.set_cookie(**rt.model_dump())
    return at


@auth_router.post(
    "/token/refresh/",
    summary="Refresh access token",
    response_model=AccessToken,
)
async def refresh(
    response: Response,
    refresh_payload: Annotated[RefreshPayload, Depends(get_refresh_payload)],
    fingerprint: Annotated[str, Depends(get_fingerprint)],
    redis: Annotated[Redis, Depends(get_redis_client)],
) -> AccessToken:
    now = datetime.now().timestamp()
    ttl = int(refresh_payload.exp - now)

    if ttl <= 24 * 60 * 60:
        await blacklist_repo.add(redis, refresh_payload)
        refresh_payload = RefreshPayload(
            sub=refresh_payload.sub, fgp=fingerprint
        )

    access_payload = AccessPayload(sub=refresh_payload.sub)
    rt, at = token_response(refresh_payload, access_payload)
    response.set_cookie(**rt.model_dump())
    return at


@auth_router.post(
    "/token/revoke/",
    response_class=ORJSONResponse,
    summary="Revoke refresh token",
)
async def revoke(
    response: Response,
    refresh_payload: Annotated[RefreshPayload, Depends(get_refresh_payload)],
    redis: Annotated[Redis, Depends(get_redis_client)],
):
    await blacklist_repo.add(redis, refresh_payload)
    response.delete_cookie(key=settings.refresh_token_cookie)
    return {"ok": True}


@auth_router.get(
    "/token/validate/",
    summary="Validate access token",
)
async def validate(
    access_payload: Annotated[AccessPayload, Depends(get_access_payload)],
):
    return ORJSONResponse(
        content={"ok": True},
        headers={
            "X-User-Id": access_payload.sub,
        },
    )
