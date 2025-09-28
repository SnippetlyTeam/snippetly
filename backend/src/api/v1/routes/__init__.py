from fastapi import APIRouter

from .auth import router as auth_router
from .auth_password import router as password_router
from .auth_registration import router as registration_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(registration_router)
v1_router.include_router(auth_router)
v1_router.include_router(password_router)
