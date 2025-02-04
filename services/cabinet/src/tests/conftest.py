import pytest
import pytest_asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient, AsyncMongoMockCollection  # type: ignore

load_dotenv(dotenv_path="src/tests/.env.test")


@pytest.fixture(scope="session")
def mongo_client() -> AsyncMongoMockClient:
    return AsyncMongoMockClient()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def session_override(app: FastAPI, mongo_client: AsyncMongoMockClient):
    from dependencies.store import get_maps_collection

    async def override_get_maps_collection() -> AsyncMongoMockCollection:
        return mongo_client["tests"]["maps"]

    app.dependency_overrides[get_maps_collection] = override_get_maps_collection


@pytest.fixture(scope="session", autouse=True)
def app() -> FastAPI:
    from main import app as current_app

    return current_app


@pytest.fixture(scope="function")
def client(app):
    with TestClient(app) as c:
        yield c
