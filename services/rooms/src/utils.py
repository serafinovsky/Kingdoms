from sqids import Sqids

from settings import settings


def make_room_key(pk: int) -> str:
    sqids = Sqids(min_length=3, alphabet=settings.alphabet)
    return sqids.encode([pk])
