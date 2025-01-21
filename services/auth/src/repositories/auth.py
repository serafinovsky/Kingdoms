from datetime import datetime

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app_types.common import Provider
from models.auth import LoginHistory, User
from repositories.base import RepositoryDB
from schemas.auth import LoginInfo, TokenMeta, UserCreate, UserUpdate


class RepositoryUser(RepositoryDB[User, UserCreate, UserUpdate]):
    """Repository for handling User model operations."""

    async def get_by_external_id_and_provider(
        self, db: AsyncSession, external_id: str, provider: Provider
    ) -> User:
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


class JWTBlacklistRepository:
    """Repository for managing JWT token blacklisting using Redis."""

    def __init__(self):
        self._key_prefix = "blacklist:token:"

    def _get_key(self, jti: str) -> str:
        """
        Generate a Redis key for a given JWT ID (jti).

        Args:
            jti (str): The JWT ID.

        Returns:
            str: The Redis key.
        """
        return f"{self._key_prefix}{jti}"

    async def add(self, client: Redis, token_metadata: TokenMeta) -> bool:
        """
        Add a JWT token to the blacklist.

        Args:
            client (Redis): The Redis client.
            token_metadata (TokenMeta): Metadata of the token to be
            blacklisted.

        Returns:
            bool: True if the token was successfully blacklisted,
            False if the token has already expired.
        """
        key = self._get_key(token_metadata.jti)
        now = datetime.now().timestamp()
        ttl = int(token_metadata.exp - now)
        if ttl <= 0:
            return False

        await client.setex(name=key, time=ttl, value="")
        return True

    async def is_blacklisted(self, client: Redis, jti: str) -> bool:
        """
        Check if a JWT token is blacklisted.

        Args:
            client (Redis): The Redis client.
            jti (str): The JWT ID to check.

        Returns:
            bool: True if the token is blacklisted, otherwise False.
        """
        key = self._get_key(jti)
        return bool(await client.exists(key))


blacklist_repo = JWTBlacklistRepository()
user_repo = RepositoryUser()
login_repo = RepositoryLoginHistory()
