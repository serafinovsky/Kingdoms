from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.store import get_pg_autocommit_session
from models.auth import Profile
from repositories.profile import profile_repo


async def get_profile_or_401(
    user_id: Annotated[str, Header(alias="X-User-Id")],
    db: Annotated[AsyncSession, Depends(get_pg_autocommit_session)],
) -> Profile:
    profile = await profile_repo.get_by_user_id(db, int(user_id))
    if not profile:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return profile
