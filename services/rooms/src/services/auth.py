import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from logger import get_logger
from settings import settings

logger = get_logger(__name__)


@retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
async def validate_token(token: str) -> bool:
    url = f"{settings.internal_url}/api/v1/auth/token/validate/"
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        response = await client.get(url, headers=headers)
        return response.status_code == 200
