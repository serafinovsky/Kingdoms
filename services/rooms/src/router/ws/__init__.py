from fastapi import APIRouter

from .rooms import rooms_router

ws_router = APIRouter(prefix="/ws")
ws_router.include_router(rooms_router)
