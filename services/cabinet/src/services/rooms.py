import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from logger import get_logger
from schemas.map import MapAndMeta
from schemas.room import NewRoom
from settings import settings

logger = get_logger(__name__)


@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
async def create_external_room(map_and_meta: MapAndMeta) -> NewRoom:
    url = f"{settings.internal_url}/api/v1/rooms/"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=map_and_meta.model_dump())
        response.raise_for_status()
        return NewRoom(**response.json())
