from sqlalchemy.ext.asyncio import AsyncSession

from logger import logging
from repositories.profile import RepositoryProfile
from schemas.auth import UserData
from schemas.profile import ProfileCreate
from tasks.profile import load_avatar

logger = logging.getLogger(__name__)


async def create_profile(
    db: AsyncSession, profile_repo: RepositoryProfile, user_data: UserData, user_id: int
):
    profile_create = ProfileCreate(
        username=user_data.username,
        name=user_data.name,
        user_id=user_id,
    )
    profile = await profile_repo.create(db, profile_create)
    await load_avatar.kiq(profile.id, user_data.avatar_url)
    return profile
