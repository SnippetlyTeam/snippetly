import asyncio

from sqlalchemy.exc import SQLAlchemyError

from src.adapters.postgres.connection import get_db
from src.adapters.postgres.models import ActivationTokenModel, PasswordResetTokenModel, RefreshTokenModel
from src.adapters.postgres.repositories import TokenRepository
from src.core.utils import logger
from ..app import app


@app.task(
    name="Delete Expired Activation & Password Reset tokens",
    autoretry_for=(SQLAlchemyError,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
    retry_backoff=True,
)
def delete_expired_activation_reset_tokens() -> None:
    async def _delete_expired_tokens() -> None:
        async for session in get_db():
            activation_repo = TokenRepository(session, ActivationTokenModel)
            password_reset_repo = TokenRepository(session, PasswordResetTokenModel)
            await activation_repo.delete_expired_tokens()
            await password_reset_repo.delete_expired_tokens()
            try:
                await session.commit()
                logger.info("Expired tokens successfully deleted")
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database error occurred during token cleanup: {e}")
                raise e
            
    asyncio.run(_delete_expired_tokens())


@app.task(
    name="Delete Expired Refresh tokens",
    autoretry_for=(SQLAlchemyError,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
    retry_backoff=True,
)
def delete_expired_refresh_tokens() -> None:
    async def _delete_expired_tokens() -> None:
        async for session in get_db():
            refresh_token_repo = TokenRepository(session, RefreshTokenModel)
            await refresh_token_repo.delete_expired_tokens()
            try:
                await session.commit()
                logger.info("Expired tokens successfully deleted")
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database error occurred during token cleanup: {e}")
                raise e

    asyncio.run(_delete_expired_tokens())
