import contextlib
from typing import AsyncIterator

import redis.asyncio as redis
from redis.asyncio import Redis

from settings import settings


class RedisManager:
    def __init__(self):
        self.redis_pool = redis.ConnectionPool.from_url(
            settings.redis_dsn.unicode_string(),
            decode_responses=True,
            retry_on_timeout=True,
        )

    async def close(self) -> None:
        await self.redis_pool.aclose()

    @contextlib.asynccontextmanager
    async def client(self) -> AsyncIterator[Redis]:
        client = redis.Redis(connection_pool=self.redis_pool)
        try:
            yield client
        finally:
            await client.aclose()


redis_manager = RedisManager()
