from fastapi import APIRouter

from src.api.v1.routes.auth import router as auth_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth_router)
