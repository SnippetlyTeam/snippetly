from datetime import datetime, timedelta, timezone

import pytest_asyncio
from sqlalchemy import update, delete

from src.adapters.postgres.models import SnippetModel, LanguageEnum


@pytest_asyncio.fixture
async def setup_snippets(
    db, snippet_factory, snippet_model_repo, snippet_doc_repo, user_factory
):
    await db.execute(delete(SnippetModel))
    await db.flush()
    user1 = await user_factory.create_active(db)
    user2 = await user_factory.create_active(db)

    u1_pub_py, _ = await snippet_factory.create(
        user1,
        language=LanguageEnum.PYTHON,
        is_private=False,
        tags=["test", "python"],
    )
    u1_priv_py, _ = await snippet_factory.create(
        user1,
        language=LanguageEnum.PYTHON,
        is_private=True,
        tags=["private"],
    )
    u1_pub_js, _ = await snippet_factory.create(
        user1,
        language=LanguageEnum.JAVASCRIPT,
        is_private=False,
    )

    u2_pub_py, _ = await snippet_factory.create(
        user2,
        language=LanguageEnum.PYTHON,
        is_private=False,
        tags=["test"],
    )
    u2_priv_js, _ = await snippet_factory.create(
        user2,
        language=LanguageEnum.JAVASCRIPT,
        is_private=True,
        tags=["private"],
    )

    old_snippet_stmt = (
        update(SnippetModel)
        .where(SnippetModel.id == u1_pub_js.id)
        .values(created_at=datetime.now(timezone.utc) - timedelta(days=5))
    )
    await db.execute(old_snippet_stmt)
    await db.flush()

    return {
        "user1": user1,
        "user2": user2,
        "u1_public_py": u1_pub_py,
        "u1_private_py": u1_priv_py,
        "u1_public_js": u1_pub_js,
        "u2_public_py": u2_pub_py,
        "u2_private_js": u2_priv_js,
    }


@pytest_asyncio.fixture
async def setup_favorites(db, favorites_repo, setup_snippets):
    user1 = setup_snippets["user1"]
    user2 = setup_snippets["user2"]

    snippets = [
        setup_snippets["u1_public_py"],
        setup_snippets["u1_public_js"],
        setup_snippets["u2_public_py"],
    ]

    favorites = []
    for snippet in snippets:
        await favorites_repo.add_to_favorites(user1, snippet.uuid)
        favorites.append(snippet)
    await db.commit()

    return user1, user2, favorites
