from sqlalchemy.ext.asyncio import AsyncSession

from logger import logging
from models.auth import User as UserModel
from repositories.auth import RepositoryUser
from schemas.auth import UserCreate, UserData

logger = logging.getLogger(__name__)


async def get_or_create_user(
    db: AsyncSession,
    user_repo: RepositoryUser,
    user_data: UserData,
) -> tuple[UserModel, bool]:
    """
    Get existing user or create a new one with associated profile.

    Args:
        db: Database session
        user_repo: User repository instance
        profile_repo: Profile repository instance
        user_data: User data from OAuth provider

    Returns:
        UserModel: Existing or newly created user
    """

    user_db = await user_repo.get_by_external_id_and_provider(
        db, external_id=user_data.external_id, provider=user_data.provider
    )
    if user_db:
        return user_db, False

    user_create = UserCreate(
        provider=user_data.provider,
        external_id=user_data.external_id,
    )

    user = await user_repo.create(db, user_create)
    return user, True
