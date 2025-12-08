from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc
from src.adapters.postgres.models import LanguageEnum, SnippetModel
from src.api.v1.schemas.snippets import (
    SnippetCreateSchema,
    SnippetUpdateRequestSchema,
)


@pytest.fixture
def snippet_create_data(active_user, faker):
    return SnippetCreateSchema(
        title=faker.sentence(nb_words=3),
        language=LanguageEnum.PYTHON,
        is_private=False,
        content=faker.text(),
        description=faker.sentence(),
        tags=[faker.word(), faker.word()],
        user_id=active_user.id,
    )


@pytest.fixture
def snippet_update_data(faker):
    return SnippetUpdateRequestSchema(
        title="A Whole New Title",
        language=LanguageEnum.JAVASCRIPT,
        is_private=True,
        content="new content for the snippet",
        description="a new description",
        tags=["new", "updated"],
    )


async def get_snippet_by_title(db, title: str):
    stmt = select(SnippetModel).where(SnippetModel.title == title)
    result = await db.execute(stmt)
    return result.scalar_one()


async def test_create_snippet_success(
    db,
    snippet_service,
    snippet_doc_repo,
    snippet_model_repo,
    active_user,
    snippet_create_data,
):
    response_schema = await snippet_service.create_snippet(snippet_create_data)

    assert response_schema.title == snippet_create_data.title
    assert response_schema.content == snippet_create_data.content
    assert response_schema.username == active_user.username
    assert set(response_schema.tags) == set(snippet_create_data.tags)

    model = await snippet_model_repo.get_by_uuid(response_schema.uuid)
    assert model is not None
    assert model.title == snippet_create_data.title
    assert model.user_id == active_user.id

    document = await snippet_doc_repo.get_by_id(model.mongodb_id)
    assert document is not None
    assert document.content == snippet_create_data.content
    assert document.description == snippet_create_data.description


async def test_create_snippet_duplicate_title(
    snippet_service, active_user, snippet_create_data
):
    await snippet_service.create_snippet(snippet_create_data)

    with pytest.raises(exc.SnippetAlreadyExistsError):
        await snippet_service.create_snippet(snippet_create_data)


async def test_create_snippet_rollback_on_db_error(
    snippet_service, snippet_doc_repo, mocker, snippet_create_data
):
    mocker.patch.object(
        snippet_service._model_repo,
        "create_with_tags",
        side_effect=SQLAlchemyError("Simulated DB error"),
    )
    delete_spy = mocker.spy(snippet_service._doc_repo, "delete_document")

    with pytest.raises(SQLAlchemyError):
        await snippet_service.create_snippet(snippet_create_data)

    delete_spy.assert_called_once()


async def test_get_own_private_snippet(db, snippet_service, setup_snippets):
    user1 = setup_snippets["user1"]
    private_snippet = setup_snippets["u1_private_py"]

    response = await snippet_service.get_snippet_by_uuid(
        private_snippet.uuid, user1
    )

    assert response is not None
    assert response.uuid == private_snippet.uuid
    assert response.title == private_snippet.title
    assert response.content is not None


async def test_get_other_user_public_snippet(
    db, snippet_service, setup_snippets
):
    user1 = setup_snippets["user1"]
    other_public_snippet = setup_snippets["u2_public_py"]

    response = await snippet_service.get_snippet_by_uuid(
        other_public_snippet.uuid, user1
    )

    assert response is not None
    assert response.uuid == other_public_snippet.uuid
    assert response.title == other_public_snippet.title


async def test_get_other_user_private_snippet_no_permission(
    db, snippet_service, setup_snippets
):
    user1 = setup_snippets["user1"]
    other_private_snippet = setup_snippets["u2_private_js"]

    with pytest.raises(exc.NoPermissionError):
        await snippet_service.get_snippet_by_uuid(
            other_private_snippet.uuid, user1
        )


async def test_get_other_user_private_snippet_as_admin(
    db, snippet_service, setup_snippets, user_factory
):
    admin_user = await user_factory.create_active(db)
    admin_user.is_admin = True
    await db.flush()

    private_snippet = setup_snippets["u2_private_js"]

    response = await snippet_service.get_snippet_by_uuid(
        private_snippet.uuid, admin_user
    )

    assert response is not None
    assert response.uuid == private_snippet.uuid
    assert response.title == private_snippet.title


async def test_get_snippet_not_found_in_db(snippet_service, setup_snippets):
    user1 = setup_snippets["user1"]
    non_existent_uuid = uuid4()

    with pytest.raises(exc.SnippetNotFoundError):
        await snippet_service.get_snippet_by_uuid(non_existent_uuid, user1)


async def test_get_snippet_document_not_found(
    db, snippet_service, snippet_doc_repo, setup_snippets
):
    user1 = setup_snippets["user1"]
    snippet = setup_snippets["u1_public_py"]

    await snippet_doc_repo.delete(snippet.mongodb_id)

    with pytest.raises(exc.SnippetNotFoundError):
        await snippet_service.get_snippet_by_uuid(snippet.uuid, user1)


async def test_update_own_snippet_success(
    db, snippet_service, setup_snippets, snippet_update_data, snippet_doc_repo
):
    user1 = setup_snippets["user1"]
    snippet_to_update = setup_snippets["u1_public_py"]

    response = await snippet_service.update_snippet(
        snippet_to_update.uuid, snippet_update_data, user1
    )

    assert response.title == snippet_update_data.title
    assert response.language == snippet_update_data.language
    assert response.is_private == snippet_update_data.is_private
    assert response.content == snippet_update_data.content
    assert response.description == snippet_update_data.description
    assert set(response.tags) == set(snippet_update_data.tags)

    updated_doc = await snippet_doc_repo.get_by_id(
        snippet_to_update.mongodb_id
    )
    assert updated_doc.content == snippet_update_data.content
    assert updated_doc.description == snippet_update_data.description

    await db.refresh(snippet_to_update)
    assert snippet_to_update.title == snippet_update_data.title
    assert {tag.name for tag in snippet_to_update.tags} == set(
        snippet_update_data.tags
    )


async def test_update_other_user_snippet_no_permission(
    db, snippet_service, setup_snippets, snippet_update_data
):
    user1 = setup_snippets["user1"]
    other_snippet = setup_snippets["u2_public_py"]

    with pytest.raises(exc.NoPermissionError):
        await snippet_service.update_snippet(
            other_snippet.uuid, snippet_update_data, user1
        )


async def test_update_other_user_snippet_as_admin(
    db, snippet_service, setup_snippets, user_factory, snippet_update_data
):
    admin_user = await user_factory.create_active(db)
    admin_user.is_admin = True
    await db.flush()

    private_snippet = setup_snippets["u1_private_py"]

    response = await snippet_service.update_snippet(
        private_snippet.uuid, snippet_update_data, admin_user
    )

    assert response is not None
    assert response.title == snippet_update_data.title


async def test_update_snippet_not_found(
    snippet_service, active_user, snippet_update_data
):
    with pytest.raises(exc.SnippetNotFoundError):
        await snippet_service.update_snippet(
            uuid4(), snippet_update_data, active_user
        )
