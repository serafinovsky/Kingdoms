from typing import Annotated

from fastapi import Header, HTTPException

not_access = HTTPException(
    status_code=401,
    detail="Invalid authentication token",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_profile_id_or_401(
    profile_id: Annotated[str | None, Header(alias="X-User-Id")],
) -> int:
    if not profile_id:
        raise not_access

    try:
        return int(profile_id)
    except (TypeError, ValueError):
        raise not_access
