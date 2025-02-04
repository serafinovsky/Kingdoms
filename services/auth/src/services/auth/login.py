from sqlalchemy.ext.asyncio import AsyncSession

from logger import logging
from repositories.auth import RepositoryLoginHistory
from schemas.auth import LoginInfo

logger = logging.getLogger(__name__)


async def new_login(db: AsyncSession, login_repo: RepositoryLoginHistory, info: LoginInfo):
    """
    Log a new login event for a user.

    Args:
        db (AsyncSession): The database session.
        login_repo (RepositoryDB): The repository for handling login history
        operations.
        info (LoginInfo): The login information to be logged.
    """
    await login_repo.create(db, info)
