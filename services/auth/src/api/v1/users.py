from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies.user import get_profile_or_401
from logger import logging
from models.auth import Profile
from schemas.user import Profile as ProfileSchema

users_router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)


@users_router.get(
    "/me/",
    summary="Get current user profile",
    response_description="Current user's profile information",
    response_model=ProfileSchema,
)
async def get_me(profile: Annotated[Profile, Depends(get_profile_or_401)]):
    return profile
