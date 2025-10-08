from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.adapters.mongo.client import init_mongo_client
from src.api.v1.routes import v1_router
from src.core.config import get_settings
from src.core.utils.logger import setup_logger, logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logger()
    logger.info("Logger Initialized")
    await init_mongo_client()
    logger.info("MongoDB Initialized")
    yield


app = FastAPI(
    title="Snippetly - API",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=settings.PROJECT_ROOT / "static"),
    name="static"
)
app.include_router(v1_router, prefix="/api")
