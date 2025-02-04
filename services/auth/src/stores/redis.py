import contextlib
from typing import AsyncIterator

import redis.asyncio as redis
from redis.asyncio import Redis

from settings import settings


class RedisManager:
    def __init__(self):
        """
        Initialize the RedisManager with a connection pool.

        The Redis connection URL is retrieved from the application settings.
        """
        self.redis_pool = redis.ConnectionPool.from_url(
            settings.redis_dsn.unicode_string(),
            decode_responses=True,
            retry_on_timeout=True,
        )

    async def close(self) -> None:
        """
        Close the Redis connection pool and clean up resources.

        This method should be called when the RedisManager is no longer needed.
        """
        await self.redis_pool.aclose()

    @contextlib.asynccontextmanager
    async def client(self) -> AsyncIterator[Redis]:
        """
        Provide an asynchronous Redis client from the connection pool.

        Yields:
            Redis: An asynchronous Redis client.

        Ensures:
            The client is properly closed after use.
        """
        client = redis.Redis(connection_pool=self.redis_pool)
        try:
            yield client
        finally:
            await client.aclose()


redis_manager = RedisManager()
