from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app_types.common import Provider
from models.auth import LoginHistory, User
from repositories.base import RepositoryDB
from schemas.auth import LoginInfo, UserCreate, UserUpdate


class RepositoryUser(RepositoryDB[User, UserCreate, UserUpdate]):
    """Repository for handling User model operations."""

    async def get_by_external_id_and_provider(
        self, db: AsyncSession, external_id: str, provider: Provider
    ) -> User | None:
        """
        Retrieve a user by their external ID and provider.

        Args:
            db (AsyncSession): The database session.
            external_id (str): The external ID of the user.
            provider (Provider): The provider associated with the user.

        Returns:
            User: The user object if found, otherwise None.
        """
        stmt = select(self._model).where(
            User.external_id == external_id,
            User.provider == provider,
        )
        return await db.scalar(stmt)


class RepositoryLoginHistory(RepositoryDB[LoginHistory, LoginInfo, LoginInfo]):
    """Repository for handling LoginHistory model operations."""


user_repo = RepositoryUser()
login_repo = RepositoryLoginHistory()
