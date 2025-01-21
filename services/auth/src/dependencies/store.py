from typing import AsyncIterator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from stores.pg import session_manager
from stores.redis import redis_manager


async def get_pg_autocommit_session() -> AsyncIterator[AsyncSession]:
    async with session_manager.create_session() as session:
        async with session_manager.transaction(session):
            yield session


async def get_redis_client() -> AsyncIterator[Redis]:
    async with redis_manager.client() as client:
        yield client
