from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select

from src.adapters.postgres.models import (
    SnippetFavoritesModel,
    SnippetModel,
    LanguageEnum,
)
from src.api.v1.schemas.snippets import FavoritesSortingEnum
from src.core import exceptions as exc


async def test_add_to_favorites_success(
    db,
    favorites_repo,
    snippet_factory,
    snippet_model_repo,
    snippet_doc_repo,
    active_user,
):
    snippet, _ = await snippet_factory.create(active_user)
    await favorites_repo.add_to_favorites(active_user, snippet.uuid)
    await db.commit()

    query = select(SnippetFavoritesModel).where(
        SnippetFavoritesModel.user_id == active_user.id,
        SnippetFavoritesModel.snippet_id == snippet.id,
    )
    result = await db.execute(query)
    favorite = result.scalar_one_or_none()

    assert favorite is not None
    assert favorite.user_id == active_user.id
    assert favorite.snippet_id == snippet.id


async def test_add_to_favorites_already_exists(
    db,
    favorites_repo,
    snippet_factory,
    snippet_model_repo,
    snippet_doc_repo,
    active_user,
):
    snippet, _ = await snippet_factory.create(active_user)
    await favorites_repo.add_to_favorites(active_user, snippet.uuid)
    await db.commit()

    with pytest.raises(exc.FavoritesAlreadyError):
        await favorites_repo.add_to_favorites(active_user, snippet.uuid)


async def test_add_to_favorites_snippet_not_found(favorites_repo, active_user):
    with pytest.raises(exc.SnippetNotFoundError):
        await favorites_repo.add_to_favorites(active_user, uuid4())


async def test_remove_from_favorites_success(
    db,
    favorites_repo,
    snippet_factory,
    snippet_model_repo,
    snippet_doc_repo,
    active_user,
):
    snippet, _ = await snippet_factory.create(active_user)
    await favorites_repo.add_to_favorites(active_user, snippet.uuid)
    await db.commit()

    await favorites_repo.remove_from_favorites(active_user, snippet.uuid)
    await db.commit()

    query = select(SnippetFavoritesModel).where(
        SnippetFavoritesModel.user_id == active_user.id,
        SnippetFavoritesModel.snippet_id == snippet.id,
    )
    result = await db.execute(query)
    favorite = result.scalar_one_or_none()

    assert favorite is None


async def test_remove_from_favorites_not_exists(
    db,
    favorites_repo,
    snippet_factory,
    snippet_model_repo,
    snippet_doc_repo,
    active_user,
):
    snippet, _ = await snippet_factory.create(active_user)
    with pytest.raises(exc.FavoritesAlreadyError):
        await favorites_repo.remove_from_favorites(active_user, snippet.uuid)


async def test_remove_from_favorites_snippet_not_found(
    favorites_repo, active_user
):
    with pytest.raises(exc.SnippetNotFoundError):
        await favorites_repo.remove_from_favorites(active_user, uuid4())


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


async def test_get_favorites_paginated_basic(favorites_repo, setup_favorites):
    user1, _, _ = setup_favorites

    favorites, total = await favorites_repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.DATE_ADDED,
    )

    assert total == len(favorites)
    assert all(isinstance(s, SnippetModel) for s in favorites)
    assert all(
        f.is_private is False or f.user_id == user1.id for f in favorites
    )


async def test_get_favorites_paginated_filter_by_language(
    favorites_repo, setup_favorites
):
    user1, _, _ = setup_favorites

    favorites, total = await favorites_repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.DATE_ADDED,
        language=LanguageEnum.PYTHON,
    )

    assert total > 0
    assert all(f.language == LanguageEnum.PYTHON for f in favorites)


async def test_get_favorites_paginated_filter_by_tag(
    favorites_repo, setup_favorites
):
    user1, _, _ = setup_favorites

    favorites, total = await favorites_repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.DATE_ADDED,
        tags=["test"],
    )

    assert total > 0
    assert all(any(tag.name == "test" for tag in f.tags) for f in favorites)


async def test_get_favorites_paginated_sorting_snippet_date(
    favorites_repo, setup_favorites
):
    user1, _, _ = setup_favorites

    favorites, _ = await favorites_repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.SNIPPET_DATE,
    )

    assert all(
        favorites[i].created_at >= favorites[i + 1].created_at
        for i in range(len(favorites) - 1)
    )


async def test_get_favorites_paginated_sorting_title(
    favorites_repo, setup_favorites
):
    user1, _, _ = setup_favorites

    favorites, _ = await favorites_repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.TITLE,
    )

    titles = [f.title for f in favorites]
    assert titles == sorted(titles, key=str.lower)
