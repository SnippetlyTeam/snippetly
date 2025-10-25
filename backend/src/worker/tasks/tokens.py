from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.adapters.postgres.sync_db import get_db_sync
from src.core.utils import logger
from ..app import app


def _delete_tokens(token: str, db: Session) -> None:
    now = datetime.now()
    db.execute(
        text(f"DELETE FROM {token} WHERE expires_at < :now"),
        {"now": now},
    )


@app.task(
    name="tokens.delete_expired_activation_reset",
    autoretry_for=(SQLAlchemyError,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
    retry_backoff=True,
)
def delete_expired_activation_reset_tokens() -> None:
    for session in get_db_sync():
        _delete_tokens("password_reset_tokens", session)
        _delete_tokens("activation_tokens", session)
        try:
            session.commit()
            logger.info("Expired tokens successfully deleted")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error occurred during token cleanup: {e}")
            raise e


@app.task(
    name="tokens.delete_expired_refresh",
    autoretry_for=(SQLAlchemyError,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
    retry_backoff=True,
)
def delete_expired_refresh_tokens() -> None:
    for session in get_db_sync():
        _delete_tokens("refresh_tokens", session)
        try:
            session.commit()
            logger.info("Expired tokens successfully deleted")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error occurred during token cleanup: {e}")
            raise e
