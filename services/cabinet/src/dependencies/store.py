from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from settings import settings
from stores.mongo import mongo_manager


async def get_mongo_client() -> AsyncIOMotorClient:
    return mongo_manager.get_client()


async def get_mongo_database() -> AsyncIOMotorDatabase:
    return mongo_manager.get_database()


async def get_maps_collection() -> AsyncIOMotorCollection:
    return mongo_manager.get_collection(settings.maps_collection)


async def get_rooms_collection() -> AsyncIOMotorCollection:
    return mongo_manager.get_collection(settings.rooms_collection)
