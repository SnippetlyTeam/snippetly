from fastapi import APIRouter

from .accounts import (
    registration_router,
    auth_router,
    oauth2_router,
    password_router,
    profile_router,
)
from .docs import router as docs_router
from .snippets import snippets_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(registration_router)
v1_router.include_router(auth_router)
v1_router.include_router(oauth2_router)
v1_router.include_router(password_router)
v1_router.include_router(snippets_router)
v1_router.include_router(profile_router)
