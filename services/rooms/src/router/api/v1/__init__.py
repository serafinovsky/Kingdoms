from fastapi import APIRouter

from .rooms import rooms_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(rooms_router)
