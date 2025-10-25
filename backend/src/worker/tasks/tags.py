from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from src.adapters.postgres.sync_db import get_db_sync
from src.core.utils import logger
from ..app import app


@app.task(
    name="tags.delete_unused_tags",
    autoretry_for=(SQLAlchemyError,),
    retry_kwargs={"max_retries": 3, "countdown": 10},
    retry_backoff=True,
)
def delete_unused_tags() -> None:
    for session in get_db_sync():
        session.execute(
            text(
                "DELETE FROM tags "
                "WHERE NOT EXISTS ("
                "SELECT 1 FROM snippets_tags st "
                "WHERE st.tag_id = tags.id)"
            )
        )
        try:
            session.commit()
            logger.info("Tags has been deleted successfully")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error occurred during tags cleanup: {e}")
            raise e
