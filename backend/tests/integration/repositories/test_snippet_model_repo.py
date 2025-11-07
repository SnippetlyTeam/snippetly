from datetime import date, timedelta, datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from beanie import PydanticObjectId
from sqlalchemy import select
from sqlalchemy import update

import src.core.exceptions as exc
from src.adapters.postgres.models import LanguageEnum, TagModel
from src.adapters.postgres.models import SnippetModel

snippet_data = {
    "title": "Test Snippet with Tags",
    "language": LanguageEnum.PYTHON,
    "is_private": False,
}


@pytest.fixture
def mongodb_id():
    return PydanticObjectId()


async def test_create_with_new_tags(
    db, snippet_model_repo, active_user, mongodb_id, faker
):
    tag_names = [faker.unique.word() for _ in range(3)]

    snippet = await snippet_model_repo.create_with_tags(
        **snippet_data,
        tag_names=tag_names,
        mongodb_id=mongodb_id,
        user_id=active_user.id,
    )
    await db.flush()

    assert snippet.id is not None
    assert snippet.title == snippet_data["title"]
    assert len(snippet.tags) == 3
    assert {tag.name for tag in snippet.tags} == set(tag_names)

    for tag_name in tag_names:
        stmt = select(TagModel).where(TagModel.name == tag_name)
        result = await db.execute(stmt)
        tag = result.scalar_one()
        assert tag is not None


async def test_create_with_existing_tags(
    db, snippet_model_repo, active_user, mongodb_id, faker
):
    existing_tags = [TagModel(name=faker.unique.word()) for _ in range(2)]
    db.add_all(existing_tags)
    await db.flush()
    tag_names = [tag.name for tag in existing_tags]

    snippet = await snippet_model_repo.create_with_tags(
        **snippet_data,
        tag_names=tag_names,
        mongodb_id=mongodb_id,
        user_id=active_user.id,
    )
    await db.flush()

    assert snippet.id is not None
    assert len(snippet.tags) == 2
    assert {tag.name for tag in snippet.tags} == set(tag_names)

    stmt = select(TagModel).where(TagModel.name.in_(tag_names))
    result = await db.execute(stmt)
    tags_from_db = result.scalars().all()
    assert len(tags_from_db) == 2
    assert {tag.id for tag in tags_from_db} == {
        tag.id for tag in existing_tags
    }


async def test_create_with_mixed_tags(
    db, snippet_model_repo, active_user, mongodb_id, faker
):
    existing_tag = TagModel(name=faker.unique.word())
    db.add(existing_tag)
    await db.flush()

    new_tag_name = faker.unique.word()
    tag_names = [existing_tag.name, new_tag_name]

    snippet = await snippet_model_repo.create_with_tags(
        **snippet_data,
        tag_names=tag_names,
        mongodb_id=mongodb_id,
        user_id=active_user.id,
    )
    await db.flush()

    assert snippet.id is not None
    assert len(snippet.tags) == 2
    assert {tag.name for tag in snippet.tags} == set(tag_names)

    stmt = select(TagModel).where(TagModel.name == new_tag_name)
    result = await db.execute(stmt)
    new_tag_from_db = result.scalar_one()
    assert new_tag_from_db is not None
    assert new_tag_from_db.id is not None

    assert existing_tag in snippet.tags


async def test_create_with_no_tags(
    db, snippet_model_repo, active_user, mongodb_id
):
    snippet = await snippet_model_repo.create_with_tags(
        **snippet_data,
        tag_names=[],
        mongodb_id=mongodb_id,
        user_id=active_user.id,
    )
    await db.flush()

    assert snippet.id is not None
    assert len(snippet.tags) == 0


async def test_get_paginated_default_visibility(
    snippet_model_repo, setup_snippets
):
    user1, _ = setup_snippets
    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=10, current_user_id=user1.id
    )
    assert total == 4
    titles = {s.title for s in snippets}
    assert "U1 Public Python" in titles
    assert "U1 Private Python" in titles
    assert "U1 Public JS" in titles
    assert "U2 Public Python" in titles
    assert "U2 Private JS" not in titles


async def test_get_paginated_public_only(snippet_model_repo, setup_snippets):
    user1, _ = setup_snippets
    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=10, current_user_id=user1.id, visibility="public"
    )
    assert total == 3
    titles = {s.title for s in snippets}
    assert "U1 Public Python" in titles
    assert "U1 Public JS" in titles
    assert "U2 Public Python" in titles


async def test_get_paginated_private_only(snippet_model_repo, setup_snippets):
    user1, _ = setup_snippets
    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=10, current_user_id=user1.id, visibility="private"
    )
    assert total == 1
    assert snippets[0].title == "U1 Private Python"


async def test_get_paginated_filter_by_language(
    snippet_model_repo, setup_snippets
):
    user1, _ = setup_snippets
    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0,
        limit=10,
        current_user_id=user1.id,
        language=LanguageEnum.PYTHON,
    )
    assert total == 3
    titles = {s.title for s in snippets}
    assert "U1 Public Python" in titles
    assert "U1 Private Python" in titles
    assert "U2 Public Python" in titles


async def test_get_paginated_filter_by_tag(snippet_model_repo, setup_snippets):
    user1, _ = setup_snippets
    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=10, current_user_id=user1.id, tags=["test"]
    )
    assert total == 2
    titles = {s.title for s in snippets}
    assert "U1 Public Python" in titles
    assert "U2 Public Python" in titles


async def test_get_paginated_filter_by_username(
    snippet_model_repo, setup_snippets
):
    user1, user2 = setup_snippets
    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=10, current_user_id=user1.id, username="user2"
    )
    assert total == 1
    assert snippets[0].title == "U2 Public Python"


async def test_get_paginated_pagination(snippet_model_repo, setup_snippets):
    user1, _ = setup_snippets
    snippets_p1, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=2, current_user_id=user1.id
    )
    assert total == 4
    assert len(snippets_p1) == 2

    snippets_p2, total_p2 = await snippet_model_repo.get_snippets_paginated(
        offset=2, limit=2, current_user_id=user1.id
    )
    assert total_p2 == 4
    assert len(snippets_p2) == 2

    ids_p1 = {s.id for s in snippets_p1}
    ids_p2 = {s.id for s in snippets_p2}
    assert not ids_p1.intersection(ids_p2)


async def test_get_paginated_filter_by_date(
    snippet_model_repo, setup_snippets
):
    user1, _ = setup_snippets

    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0,
        limit=10,
        current_user_id=user1.id,
        created_after=date.today() - timedelta(days=2),
    )
    assert total == 3
    titles = {s.title for s in snippets}
    assert "U1 Public JS" not in titles

    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0,
        limit=10,
        current_user_id=user1.id,
        created_before=date.today() - timedelta(days=3),
    )
    assert total == 1
    assert snippets[0].title == "U1 Public JS"


async def test_get_by_uuid(snippet_model_repo, setup_snippets):
    user1, _ = setup_snippets
    stmt = select(SnippetModel).where(
        SnippetModel.user_id == user1.id,
        SnippetModel.title == "U1 Public Python",
    )
    result = await snippet_model_repo._db.execute(stmt)
    existing_snippet = result.scalar_one()

    found_snippet = await snippet_model_repo.get_by_uuid(existing_snippet.uuid)
    assert found_snippet is not None
    assert found_snippet.id == existing_snippet.id
    assert found_snippet.title == "U1 Public Python"

    not_found_snippet = await snippet_model_repo.get_by_uuid(uuid4())
    assert not_found_snippet is None


async def test_get_by_uuid_with_tags(snippet_model_repo, setup_snippets):
    user1, _ = setup_snippets
    stmt = select(SnippetModel).where(
        SnippetModel.user_id == user1.id,
        SnippetModel.title == "U1 Public Python",
    )
    result = await snippet_model_repo._db.execute(stmt)
    existing_snippet = result.scalar_one()

    found_snippet = await snippet_model_repo.get_by_uuid_with_tags(
        existing_snippet.uuid
    )
    assert found_snippet is not None
    assert found_snippet.id == existing_snippet.id

    assert len(found_snippet.tags) == 2
    assert {tag.name for tag in found_snippet.tags} == {"test", "python"}


async def test_get_by_user(snippet_model_repo, setup_snippets):
    user1, user2 = setup_snippets

    user1_snippets = await snippet_model_repo.get_by_user(user1.id)
    assert user1_snippets is not None
    assert len(user1_snippets) == 3
    user1_titles = {s.title for s in user1_snippets}
    assert "U1 Public Python" in user1_titles
    assert "U1 Private Python" in user1_titles
    assert "U1 Public JS" in user1_titles

    user2_snippets = await snippet_model_repo.get_by_user(user2.id)
    assert user2_snippets is not None
    assert len(user2_snippets) == 2
    user2_titles = {s.title for s in user2_snippets}
    assert "U2 Public Python" in user2_titles
    assert "U2 Private JS" in user2_titles

    no_snippets_user_id = 999
    no_snippets_result = await snippet_model_repo.get_by_user(
        no_snippets_user_id
    )
    assert no_snippets_result == []


async def test_get_by_title(snippet_model_repo, setup_snippets):
    user1, user2 = setup_snippets
    title_user1 = "U1 Public Python"
    title_user2 = "U2 Public Python"

    found_snippet = await snippet_model_repo.get_by_title(
        title_user1, user1.id
    )
    assert found_snippet is not None
    assert found_snippet.title == title_user1
    assert found_snippet.user_id == user1.id

    not_found_snippet = await snippet_model_repo.get_by_title(
        title_user2, user1.id
    )
    assert not_found_snippet is None

    not_found_snippet = await snippet_model_repo.get_by_title(
        "Non Existent", user1.id
    )
    assert not_found_snippet is None


async def test_get_by_title_list(snippet_model_repo, setup_snippets):
    user1, user2 = setup_snippets

    public_snippets = await snippet_model_repo.get_by_title_list(
        "Public", user1.id
    )
    assert len(public_snippets) == 3
    public_titles = {s.title for s in public_snippets}
    assert "U1 Public Python" in public_titles
    assert "U1 Public JS" in public_titles
    assert "U2 Public Python" in public_titles

    private_snippets = await snippet_model_repo.get_by_title_list(
        "Private", user1.id
    )
    assert len(private_snippets) == 1
    assert private_snippets[0].title == "U1 Private Python"

    python_snippets = await snippet_model_repo.get_by_title_list(
        "Python", user1.id
    )
    assert len(python_snippets) == 3
    python_titles = {s.title for s in python_snippets}
    assert "U1 Public Python" in python_titles
    assert "U1 Private Python" in python_titles
    assert "U2 Public Python" in python_titles

    limited_snippets = await snippet_model_repo.get_by_title_list(
        "Python", user1.id, limit=1
    )
    assert len(limited_snippets) == 1


async def test_delete(db, snippet_model_repo, setup_snippets):
    user1, _ = setup_snippets
    stmt = select(SnippetModel).where(
        SnippetModel.user_id == user1.id,
        SnippetModel.title == "U1 Public Python",
    )
    result = await db.execute(stmt)
    snippet_to_delete = result.scalar_one()
    uuid_to_delete = snippet_to_delete.uuid

    await snippet_model_repo.delete(uuid_to_delete)
    await db.flush()

    deleted_snippet = await snippet_model_repo.get_by_uuid(uuid_to_delete)
    assert deleted_snippet is None

    try:
        await snippet_model_repo.delete(uuid4())
        await db.flush()
    except Exception as e:
        pytest.fail(
            f"Deleting a non-existent snippet raised an exception: {e}"
        )


async def test_update_success(db, snippet_model_repo, setup_snippets):
    user1, _ = setup_snippets
    stmt = select(SnippetModel).where(
        SnippetModel.user_id == user1.id,
        SnippetModel.title == "U1 Public Python",
    )
    result = await db.execute(stmt)
    snippet_to_update = result.scalar_one()
    uuid_to_update = snippet_to_update.uuid

    update_data = {
        "title": "Updated Title",
        "language": LanguageEnum.JAVASCRIPT,
        "is_private": True,
    }

    updated_snippet = await snippet_model_repo.update(
        uuid_to_update, **update_data
    )

    assert updated_snippet.title == update_data["title"]
    assert updated_snippet.language == update_data["language"]
    assert updated_snippet.is_private == update_data["is_private"]

    await db.flush()
    await db.refresh(updated_snippet)

    refetched_snippet = await snippet_model_repo.get_by_uuid(uuid_to_update)
    assert refetched_snippet is not None
    assert refetched_snippet.title == update_data["title"]
    assert refetched_snippet.language == update_data["language"]
    assert refetched_snippet.is_private == update_data["is_private"]


async def test_update_partial(db, snippet_model_repo, setup_snippets):
    user1, _ = setup_snippets
    stmt = select(SnippetModel).where(
        SnippetModel.user_id == user1.id,
        SnippetModel.title == "U1 Public Python",
    )
    result = await db.execute(stmt)
    snippet_to_update = result.scalar_one()
    uuid_to_update = snippet_to_update.uuid
    original_language = snippet_to_update.language

    updated_snippet = await snippet_model_repo.update(
        uuid_to_update, title="Partially Updated Title"
    )

    assert updated_snippet.title == "Partially Updated Title"
    assert updated_snippet.language == original_language


async def test_update_not_found(snippet_model_repo):
    non_existent_uuid = uuid4()
    with pytest.raises(exc.SnippetNotFoundError):
        await snippet_model_repo.update(non_existent_uuid, title="Won't work")
