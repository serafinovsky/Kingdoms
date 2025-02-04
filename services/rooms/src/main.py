from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from logger import logging
from router.api import api_router
from router.ws import ws_router
from stores.redis import redis_manager

logger = logging.getLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await redis_manager.close()


app = FastAPI(
    default_response_class=ORJSONResponse,
    docs_url="/api/rooms/docs/",
    openapi_url="/api/rooms/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ws_router)
app.include_router(api_router)
