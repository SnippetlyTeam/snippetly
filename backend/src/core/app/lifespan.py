from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.adapters.mongo.client import init_mongo_client
from src.core.utils.logger import setup_logger, logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logger()
    logger.info("Logger Initialized")

    await init_mongo_client()
    logger.info("MongoDB Initialized")

    yield
