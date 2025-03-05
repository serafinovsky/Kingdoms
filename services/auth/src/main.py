from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.logging import LoggingIntegration

from logger import logging
from router.api import api_router
from settings import settings
from stores.pg import session_manager
from stores.redis import redis_manager

logger = logging.getLogger()


if settings.sentry_dsn:
    env = "dev" if settings.debug else "prod"
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0.1,
        profiles_sample_rate=0,
        environment=env,
        integrations=[LoggingIntegration(event_level=logging.ERROR)],
        _experiments={
            "continuous_profiling_auto_start": False,
        },
    )
    sentry_sdk.set_tag("service", "auth")
    sentry_sdk.set_tag("env", env)


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


app.include_router(api_router)
