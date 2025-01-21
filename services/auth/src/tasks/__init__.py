# from huey import RedisHuey

from taskiq_redis import ListQueueBroker

from settings import settings

# broker = RedisMemoryBroker(url=settings.redis_dsn.unicode_string())
# taskiq = TaskIQ(broker=broker)

broker = ListQueueBroker(url=settings.redis_dsn.unicode_string())

# huey = RedisHuey(url=settings.redis_dsn.unicode_string())

from .user import *
