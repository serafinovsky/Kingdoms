from taskiq_redis import ListQueueBroker

from settings import settings

broker = ListQueueBroker(url=settings.redis_dsn.unicode_string())

from .profile import *  # noqa: E402, F403
