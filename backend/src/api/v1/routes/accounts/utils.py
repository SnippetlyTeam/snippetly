from fastapi import Response

from src.core.config import get_settings

settings = get_settings()


def set_refresh_token(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=True,
        max_age=settings.REFRESH_TOKEN_LIFE * 24 * 60 * 60,
        path="/api/v1/auth",
    )
