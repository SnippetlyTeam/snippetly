from fastapi import APIRouter

from .auth_login import router as auth_router
from .auth_password import router as password_router
from .auth_registration import router as registration_router
from .oauth2 import router as oauth2_router
from .snippets import router as snippets_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(registration_router)
v1_router.include_router(auth_router)
v1_router.include_router(oauth2_router)
v1_router.include_router(password_router)
v1_router.include_router(snippets_router)
