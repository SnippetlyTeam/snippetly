from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.core.config import Settings


def setup_middlewares(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['http://localhost:5173'],
        allow_methods=["*"],
        allow_credentials=True,
        allow_headers=["*"],
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY_ACCESS.get_secret_value(),
    )
