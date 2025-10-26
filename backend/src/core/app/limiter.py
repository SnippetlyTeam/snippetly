from fastapi import FastAPI
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.core.config import Settings

limiter = Limiter(key_func=get_remote_address)


def setup_limiter(app: FastAPI, settings: Settings) -> None:
    limiter._storage_uri = settings.redis_url
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, limiter.slowapi_startup)  # type: ignore
