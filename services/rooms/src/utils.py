import time
from contextlib import contextmanager

from prometheus_client import Histogram
from sqids import Sqids

from settings import settings


def make_room_key(pk: int) -> str:
    sqids = Sqids(min_length=3, alphabet=settings.alphabet)
    return sqids.encode([pk])


@contextmanager
def measure_time(histogram: Histogram, labels: dict):
    """Context manager for measuring execution time"""
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        histogram.labels(**labels).observe(duration)
