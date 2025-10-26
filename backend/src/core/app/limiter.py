from fastapi import FastAPI
from fastapi.requests import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.core.config import Settings

limiter = Limiter(key_func=get_remote_address, headers_enabled=True)


def setup_limiter(app: FastAPI, settings: Settings) -> None:
    limiter._storage_uri = settings.redis_url
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore


def key_func_per_user(request: Request) -> str:
    user = getattr(request, "current_user", None)
    if user:
        return str(user.id)
    return get_remote_address(request)
