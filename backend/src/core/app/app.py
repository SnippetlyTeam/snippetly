from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.admin import admin
from src.api.v1.routes import v1_router, docs_router
from src.middleware.prometheus import metrics_endpoint
from src.core.config import get_settings
from .lifespan import lifespan
from .limiter import setup_limiter
from .middleware import setup_middlewares


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Snippetly - API",
        version="1.0.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    setup_middlewares(app, settings)
    setup_limiter(app, settings)

    admin.mount_to(app)

    app.mount(
        "/static",
        StaticFiles(directory=settings.PROJECT_ROOT / "static"),
        name="static",
    )

    app.include_router(docs_router, prefix="/api")
    app.include_router(v1_router, prefix="/api")

    app.get("/api/metrics")(metrics_endpoint)

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok"}

    return app
