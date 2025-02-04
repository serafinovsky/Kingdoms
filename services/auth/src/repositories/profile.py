from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.auth import Profile
from repositories.base import RepositoryDB
from schemas.profile import ProfileCreate, ProfileUpdate


class RepositoryProfile(RepositoryDB[Profile, ProfileCreate, ProfileUpdate]):
    """
    Repository for handling Profile model operations.

    Inherits from RepositoryDB and provides additional methods specific
    to the Profile model.
    """

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> Profile | None:
        """
        Retrieve a profile by its associated user ID.

        Args:
            db (AsyncSession): The database session.
            user_id (int): The ID of the user associated with the profile.

        Returns:
            Optional[Profile]: The profile object if found, otherwise None.

        """
        stmt = select(self._model).where(Profile.user_id == user_id)
        return await db.scalar(stmt)


profile_repo = RepositoryProfile()
