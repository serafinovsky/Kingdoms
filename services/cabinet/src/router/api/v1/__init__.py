__all__ = ["v1_router"]

from fastapi import APIRouter

from .cabinet import cabinet_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(cabinet_router)
