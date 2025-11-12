from datetime import date, timedelta
from uuid import uuid4

import pytest
from beanie import PydanticObjectId
from sqlalchemy import select

import src.core.exceptions as exc
from src.adapters.postgres.models import LanguageEnum, TagModel

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
    user1 = setup_snippets["user1"]

    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=10, current_user_id=user1.id
    )

    assert total == 4

    user1_ids = {
        setup_snippets["u1_public_py"].id,
        setup_snippets["u1_private_py"].id,
        setup_snippets["u1_public_js"].id,
    }
    user2_public_id = setup_snippets["u2_public_py"].id

    assert any(s.id in user1_ids for s in snippets)
    assert all(not s.is_private or s.user_id == user1.id for s in snippets)
    assert all(
        s.language in [LanguageEnum.PYTHON, LanguageEnum.JAVASCRIPT]
        for s in snippets
    )
    assert any(s.id == user2_public_id for s in snippets)


async def test_get_paginated_public_only(snippet_model_repo, setup_snippets):
    user1 = setup_snippets["user1"]

    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=10, current_user_id=user1.id, visibility="public"
    )

    assert total == 3
    assert all(not s.is_private for s in snippets)


async def test_get_paginated_private_only(snippet_model_repo, setup_snippets):
    user1 = setup_snippets["user1"]

    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=10, current_user_id=user1.id, visibility="private"
    )
    assert total == 1
    assert snippets[0].is_private
    assert snippets[0].user_id == user1.id


async def test_get_paginated_filter_by_language(
    snippet_model_repo, setup_snippets
):
    user1 = setup_snippets["user1"]

    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0,
        limit=10,
        current_user_id=user1.id,
        language=LanguageEnum.PYTHON,
    )
    assert total == 3
    assert all(s.language == LanguageEnum.PYTHON for s in snippets)


async def test_get_paginated_filter_by_tag(snippet_model_repo, setup_snippets):
    user1 = setup_snippets["user1"]

    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=10, current_user_id=user1.id, tags=["test"]
    )

    assert total == 2
    assert all("test" in {t.name for t in s.tags} for s in snippets)


async def test_get_paginated_filter_by_username(
    snippet_model_repo, setup_snippets
):
    user1 = setup_snippets["user1"]
    user2 = setup_snippets["user2"]

    snippets, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=10, current_user_id=user1.id, username=user2.username
    )

    assert total == 1
    assert snippets[0].user_id == user2.id
    assert not snippets[0].is_private


async def test_get_paginated_pagination(snippet_model_repo, setup_snippets):
    user1 = setup_snippets["user1"]

    snippets_p1, total = await snippet_model_repo.get_snippets_paginated(
        offset=0, limit=2, current_user_id=user1.id
    )
    snippets_p2, total_p2 = await snippet_model_repo.get_snippets_paginated(
        offset=2, limit=2, current_user_id=user1.id
    )

    assert total == total_p2 == 4
    assert len(snippets_p1) == 2
    assert len(snippets_p2) == 2
    assert not {s.id for s in snippets_p1}.intersection(
        {s.id for s in snippets_p2}
    )


async def test_get_paginated_filter_by_date(
    snippet_model_repo, setup_snippets
):
    user1 = setup_snippets["user1"]

    (
        recent_snippets,
        total_recent,
    ) = await snippet_model_repo.get_snippets_paginated(
        offset=0,
        limit=10,
        current_user_id=user1.id,
        created_after=date.today() - timedelta(days=2),
    )
    old_snippets, total_old = await snippet_model_repo.get_snippets_paginated(
        offset=0,
        limit=10,
        current_user_id=user1.id,
        created_before=date.today() - timedelta(days=3),
    )

    assert total_recent == 3
    assert total_old == 1
    assert all(
        s.created_at.date() < (date.today() - timedelta(days=3))
        for s in old_snippets
    )


async def test_get_by_uuid(snippet_model_repo, setup_snippets):
    snippet = setup_snippets["u1_public_py"]

    found = await snippet_model_repo.get_by_uuid(snippet.uuid)
    assert found is not None
    assert found.id == snippet.id

    not_found = await snippet_model_repo.get_by_uuid(uuid4())
    assert not_found is None


async def test_get_by_user(snippet_model_repo, setup_snippets):
    user1 = setup_snippets["user1"]
    user2 = setup_snippets["user2"]

    user1_snippets = await snippet_model_repo.get_by_user(user1.id)
    user2_snippets = await snippet_model_repo.get_by_user(user2.id)

    assert len(user1_snippets) == 3
    assert len(user2_snippets) == 2

    no_snippets = await snippet_model_repo.get_by_user(999)
    assert no_snippets == []


async def test_get_by_title(snippet_model_repo, setup_snippets):
    snippet = setup_snippets["u1_public_py"]
    user1 = setup_snippets["user1"]
    user2 = setup_snippets["user2"]

    found_snippet = await snippet_model_repo.get_by_title(
        snippet.title, user1.id
    )
    assert found_snippet is not None
    assert found_snippet.title == snippet.title
    assert found_snippet.user_id == user1.id

    not_found = await snippet_model_repo.get_by_title(snippet.title, user2.id)
    assert not_found is None

    not_found = await snippet_model_repo.get_by_title(
        "DefinitelyNotExist", user1.id
    )
    assert not_found is None


async def test_get_by_title_list(snippet_model_repo, setup_snippets):
    user1 = setup_snippets["user1"]
    user2 = setup_snippets["user2"]
    sample_snippet = setup_snippets["u1_public_py"]

    keyword = sample_snippet.title.split()[0]
    found = await snippet_model_repo.get_by_title_list(keyword, user1.id)

    assert isinstance(found, list)
    assert any(s.id == sample_snippet.id for s in found)
    assert all(isinstance(s.title, str) for s in found)

    limited = await snippet_model_repo.get_by_title_list(
        keyword, user1.id, limit=1
    )
    assert len(limited) == 1

    found_for_user2 = await snippet_model_repo.get_by_title_list(
        keyword, user2.id
    )
    assert all(
        s.user_id == user2.id or not s.is_private for s in found_for_user2
    )


async def test_delete(db, snippet_model_repo, setup_snippets):
    snippet_to_delete = setup_snippets["u1_public_py"]
    uuid_to_delete = snippet_to_delete.uuid

    await snippet_model_repo.delete(uuid_to_delete)
    await db.flush()

    deleted = await snippet_model_repo.get_by_uuid(uuid_to_delete)
    assert deleted is None

    try:
        await snippet_model_repo.delete(uuid4())
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


async def test_update_success(db, snippet_model_repo, setup_snippets):
    snippet_to_update = setup_snippets["u1_public_py"]
    uuid_to_update = snippet_to_update.uuid

    update_data = {
        "title": "Updated Title",
        "language": LanguageEnum.JAVASCRIPT,
        "is_private": True,
    }

    updated = await snippet_model_repo.update(uuid_to_update, **update_data)
    await db.flush()
    await db.refresh(updated)

    assert updated.title == "Updated Title"
    assert updated.language == LanguageEnum.JAVASCRIPT
    assert updated.is_private is True


async def test_update_partial(db, snippet_model_repo, setup_snippets):
    snippet_to_update = setup_snippets["u1_public_py"]
    uuid_to_update = snippet_to_update.uuid
    original_lang = snippet_to_update.language

    updated = await snippet_model_repo.update(
        uuid_to_update, title="Partial Title"
    )

    assert updated.title == "Partial Title"
    assert updated.language == original_lang


async def test_update_not_found(snippet_model_repo):
    with pytest.raises(exc.SnippetNotFoundError):
        await snippet_model_repo.update(uuid4(), title="Won't work")
