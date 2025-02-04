from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from settings import settings


class ConnectionManager:
    def __init__(self) -> None:
        self.client: AsyncIOMotorClient | None = None

    async def connect(self):
        if self.client is None:
            self.client = AsyncIOMotorClient(settings.mongo_dsn.unicode_string())

    async def close(self):
        if self.client:
            self.client.close()
            self.client = None

    def get_client(self) -> AsyncIOMotorClient:
        if self.client is None:
            raise RuntimeError("Database connection is not established")
        return self.client

    def get_database(self) -> AsyncIOMotorDatabase:
        return self.get_client()[settings.mongo_db]

    def get_collection(self, name: str) -> AsyncIOMotorCollection:
        return self.get_database()[name]


mongo_manager = ConnectionManager()
