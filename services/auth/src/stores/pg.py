import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from logger import logging
from settings import settings


class SessionManager:
    def __init__(self):
        """
        Initialize the SessionManager with an async database engine and
        sessionmaker.

        The database URL is retrieved from the application settings.
        """
        url = settings.pg_dsn.unicode_string()
        self._engine = create_async_engine(url, future=True, echo=settings.debug)
        self._sessionmaker = async_sessionmaker(self._engine, expire_on_commit=False)

    async def close(self) -> None:
        """
        Dispose of the database engine and clean up resources.

        This method should be called when the SessionManager is
        no longer needed.
        """
        await self._engine.dispose()

    @contextlib.asynccontextmanager
    async def create_session(self) -> AsyncIterator[AsyncSession]:
        """
        Create and yield an asynchronous database session.

        Yields:
            AsyncSession: An asynchronous database session.

        Raises:
            Exception: If an error occurs during session usage.
        """
        session: AsyncSession = self._sessionmaker()
        try:
            yield session
        except Exception as e:
            logging.error(f"Session error: {e}", exc_info=e)
            raise
        finally:
            await session.close()

    @contextlib.asynccontextmanager
    async def transaction(self, session: AsyncSession) -> AsyncIterator[None]:
        """
        Manage a database transaction.

        Args:
            session (AsyncSession): The database session to use for
            the transaction.

        Yields:
            None: The transaction context.

        Raises:
            Exception: If an error occurs during the transaction.
        """
        try:
            yield
            await session.commit()
        except Exception as e:
            await session.rollback()
            logging.exception(f"Transaction error: {e}", exc_info=e)
            raise


session_manager = SessionManager()
