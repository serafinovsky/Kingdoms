from typing import AsyncIterator

from redis.asyncio import Redis

from stores.redis import redis_manager


async def get_redis_client() -> AsyncIterator[Redis]:
    async with redis_manager.client() as client:
        yield client
