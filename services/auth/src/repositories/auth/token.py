from datetime import datetime

from redis.asyncio import Redis

from schemas.auth import TokenMeta


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
