import mimetypes
from pathlib import Path

import aiofiles
import httpx
from httpx import HTTPError

from logger import logging
from repositories.user import profile_repo
from schemas.user import ProfileUpdate
from settings import settings
from stores.pg import session_manager
from tasks import broker

logger = logging.getLogger()

mimetypes.init()

MEDIA_ROOT = Path(settings.media_root)
MEDIA_URL = settings.media_url
CHUNK_SIZE = 8192
REQUEST_TIMEOUT = 10
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit


class AvatarLoadError(Exception):
    """Custom exception for avatar loading errors."""


def get_file_name(profile_id: int, mime_type: str | None) -> Path:
    """Generate file path for avatar with appropriate extension."""
    ext = mimetypes.guess_extension(mime_type) if mime_type else ""
    ext = ext or ""
    return f"{profile_id}{ext}"


async def update_profile_avatar(profile_id: int, avatar_path: str) -> None:
    """Update user profile with avatar path."""
    async with session_manager.create_session() as session:
        async with session_manager.transaction(session):
            await profile_repo.update(
                session, profile_id, ProfileUpdate(avatar=avatar_path)
            )


async def _load_avatar_async(profile_id: int, url: str) -> None:
    """Asynchronous implementation of avatar loading."""
    try:
        MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()

                mime_type = response.headers.get("content-type")
                if not mime_type or not mime_type.startswith("image/"):
                    raise AvatarLoadError(f"Invalid content type: {mime_type}")

                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > MAX_FILE_SIZE:
                    raise AvatarLoadError("File size exceeds maximum limit")

                file_name = get_file_name(profile_id, mime_type)
                path = MEDIA_ROOT / file_name
                total_size = 0

                async with aiofiles.open(path, mode="wb") as file:
                    async for chunk in response.aiter_bytes(
                        chunk_size=CHUNK_SIZE
                    ):
                        total_size += len(chunk)
                        if total_size > MAX_FILE_SIZE:
                            raise AvatarLoadError(
                                "File size exceeds maximum limit"
                            )
                        await file.write(chunk)

        await update_profile_avatar(profile_id, f"{MEDIA_URL}{file_name}")
        logger.info(f"Successfully loaded avatar for profile {profile_id}")
    except HTTPError as e:
        logger.error(f"Failed to download avatar: {str(e)}")
        raise AvatarLoadError(f"Failed to download avatar: {str(e)}")
    except IOError as e:
        logger.error(f"Failed to save avatar: {str(e)}")
        raise AvatarLoadError(f"Failed to save avatar: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error loading avatar: {str(e)}")
        raise AvatarLoadError(f"Unexpected error loading avatar: {str(e)}")


@broker.task()
async def load_avatar(profile_id: int, url: str) -> None:
    """Task to download and save avatar image from URL."""
    await _load_avatar_async(profile_id, url)
