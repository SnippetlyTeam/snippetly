from .config import BaseAppSettings


class APISettings(BaseAppSettings):
    FRONTEND_URL: str = "http://localhost:5173"
