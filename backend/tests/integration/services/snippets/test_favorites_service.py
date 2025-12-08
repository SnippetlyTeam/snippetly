from uuid import uuid4

import pytest

from src.adapters.postgres.models import LanguageEnum
from src.api.v1.schemas.snippets import FavoritesSortingEnum
from src.core import exceptions as exc


async def test_add_to_favorites_success(
    favorites_service, snippet_factory, active_user
):
    snippet, _ = await snippet_factory.create(active_user)

    await favorites_service.add_to_favorites(active_user, snippet.uuid)

    (
        fav_snippets,
        total,
    ) = await favorites_service._repo.get_favorites_paginated(
        0, 10, active_user.id, sort_by=None
    )
    assert any(f.id == snippet.id for f in fav_snippets)


async def test_add_to_favorites_already_exists(
    favorites_service, snippet_factory, active_user
):
    snippet, _ = await snippet_factory.create(active_user)
    await favorites_service.add_to_favorites(active_user, snippet.uuid)

    with pytest.raises(exc.FavoritesAlreadyError):
        await favorites_service.add_to_favorites(active_user, snippet.uuid)


async def test_add_to_favorites_snippet_not_found(
    favorites_service, active_user
):
    with pytest.raises(exc.SnippetNotFoundError):
        await favorites_service.add_to_favorites(active_user, uuid4())


async def test_remove_from_favorites_success(
    favorites_service, snippet_factory, active_user
):
    snippet, _ = await snippet_factory.create(active_user)
    await favorites_service.add_to_favorites(active_user, snippet.uuid)

    await favorites_service.remove_from_favorites(active_user, snippet.uuid)

    (
        fav_snippets,
        total,
    ) = await favorites_service._repo.get_favorites_paginated(
        0, 10, active_user.id, sort_by=None
    )
    assert all(f.id != snippet.id for f in fav_snippets)


async def test_remove_from_favorites_not_exists(
    favorites_service, snippet_factory, active_user
):
    snippet, _ = await snippet_factory.create(active_user)

    with pytest.raises(exc.FavoritesAlreadyError):
        await favorites_service.remove_from_favorites(
            active_user, snippet.uuid
        )


async def test_remove_from_favorites_snippet_not_found(
    favorites_service, active_user
):
    with pytest.raises(exc.SnippetNotFoundError):
        await favorites_service.remove_from_favorites(active_user, uuid4())


async def test_get_favorites_paginated_basic(
    favorites_service, setup_favorites
):
    user1, _, favorites = setup_favorites

    result, total = await favorites_service._repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.DATE_ADDED,
    )

    assert total == len(favorites)
    assert all(s.id in [f.id for f in favorites] for s in result)


async def test_get_favorites_paginated_filter_by_language(
    favorites_service, setup_favorites
):
    user1, _, _ = setup_favorites

    result, total = await favorites_service._repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.DATE_ADDED,
        language=LanguageEnum.PYTHON,
    )

    assert all(s.language == LanguageEnum.PYTHON for s in result)


async def test_get_favorites_paginated_filter_by_tag(
    favorites_service, setup_favorites
):
    user1, _, _ = setup_favorites

    result, total = await favorites_service._repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.DATE_ADDED,
        tags=["test"],
    )

    assert all("test" in [t.name for t in s.tags] for s in result)


async def test_get_favorites_paginated_sorting_snippet_date(
    favorites_service, setup_favorites
):
    user1, _, _ = setup_favorites

    result, _ = await favorites_service._repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.SNIPPET_DATE,
    )

    assert all(
        result[i].created_at >= result[i + 1].created_at
        for i in range(len(result) - 1)
    )


async def test_get_favorites_paginated_sorting_title(
    favorites_service, setup_favorites
):
    user1, _, _ = setup_favorites

    result, _ = await favorites_service._repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.TITLE,
    )

    titles = [s.title for s in result]
    assert titles == sorted(titles, key=str.lower)


async def test_get_favorites_paginated_pagination(
    favorites_service, setup_favorites
):
    user1, _, _ = setup_favorites

    page1, total1 = await favorites_service._repo.get_favorites_paginated(
        offset=0,
        limit=2,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.DATE_ADDED,
    )
    page2, total2 = await favorites_service._repo.get_favorites_paginated(
        offset=2,
        limit=2,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.DATE_ADDED,
    )

    assert total1 == total2 == 3
    assert len(page1) == 2
    assert len(page2) == 1
    assert not {s.id for s in page1}.intersection({s.id for s in page2})


async def test_get_favorites_paginated_filter_by_username(
    favorites_service, setup_favorites
):
    user1, user2, _ = setup_favorites

    result, total = await favorites_service._repo.get_favorites_paginated(
        offset=0,
        limit=10,
        user_id=user1.id,
        sort_by=FavoritesSortingEnum.DATE_ADDED,
        username=user2.username,
    )

    assert all(s.user_id == user2.id for s in result)
