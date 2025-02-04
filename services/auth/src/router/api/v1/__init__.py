from fastapi import APIRouter

from .auth import auth_router
from .profile import users_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth_router)
v1_router.include_router(users_router)
