from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from logger import logging
from router.api import api_router
from stores.mongo import mongo_manager

logger = logging.getLogger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo_manager.connect()
    yield
    await mongo_manager.close()


app = FastAPI(
    default_response_class=ORJSONResponse,
    docs_url="/api/cabinet/docs/",
    openapi_url="/api/cabinet/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)
