from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from api.v1 import v1_router
from logger import logging
from stores.pg import session_manager
from stores.redis import redis_manager

logger = logging.getLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await session_manager.close()
    await redis_manager.close()


app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    docs_url="/api/auth/docs/",
    openapi_url="/api/auth/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(v1_router, prefix="/api")
