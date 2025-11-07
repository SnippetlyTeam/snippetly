from datetime import timedelta, datetime, timezone

import pytest_asyncio
from sqlalchemy import update

from src.adapters.postgres.models import LanguageEnum, SnippetModel


@pytest_asyncio.fixture
async def setup_snippets(
    db, snippet_factory, snippet_model_repo, snippet_doc_repo, user_factory
):
    user1 = await user_factory.create_active(db, username="user1")
    user2 = await user_factory.create_active(db, username="user2")

    await snippet_factory.create(
        db,
        snippet_model_repo,
        snippet_doc_repo,
        user1,
        title="U1 Public Python",
        language=LanguageEnum.PYTHON,
        is_private=False,
        tags=["test", "python"],
    )
    await snippet_factory.create(
        db,
        snippet_model_repo,
        snippet_doc_repo,
        user1,
        title="U1 Private Python",
        language=LanguageEnum.PYTHON,
        is_private=True,
        tags=["private"],
    )
    await snippet_factory.create(
        db,
        snippet_model_repo,
        snippet_doc_repo,
        user1,
        title="U1 Public JS",
        language=LanguageEnum.JAVASCRIPT,
        is_private=False,
    )

    await snippet_factory.create(
        db,
        snippet_model_repo,
        snippet_doc_repo,
        user2,
        title="U2 Public Python",
        language=LanguageEnum.PYTHON,
        is_private=False,
        tags=["test"],
    )
    await snippet_factory.create(
        db,
        snippet_model_repo,
        snippet_doc_repo,
        user2,
        title="U2 Private JS",
        language=LanguageEnum.JAVASCRIPT,
        is_private=True,
        tags=["private"],
    )

    await db.flush()

    old_snippet_stmt = (
        update(SnippetModel)
        .where(SnippetModel.title == "U1 Public JS")
        .values(created_at=datetime.now(timezone.utc) - timedelta(days=5))
    )
    await db.execute(old_snippet_stmt)

    await db.flush()

    return user1, user2
