import pytest
import pytest_asyncio
from beanie import PydanticObjectId
from pymongo.errors import PyMongoError

doc_data = {"content": "Test content", "description": "Test description"}


@pytest_asyncio.fixture
async def snippet_doc(snippet_doc_repo):
    return await snippet_doc_repo.create(content="Some content")


async def test_create_snippet_success(snippet_doc_repo):
    snippet = await snippet_doc_repo.create(**doc_data)
    assert snippet.id is not None
    assert snippet.content == doc_data["content"]
    assert snippet.description == doc_data["description"]
    assert snippet.created_at <= snippet.updated_at


async def test_create_snippet_value_error(snippet_doc_repo):
    with pytest.raises(ValueError):
        await snippet_doc_repo.create(content="")


async def test_create_pymongo_error(mocker, snippet_doc_repo):
    mock = mocker.patch(
        "src.adapters.mongo.repo.SnippetDocument.insert",
        side_effect=PyMongoError,
    )

    with pytest.raises(PyMongoError):
        await snippet_doc_repo.create(**doc_data)

    mock.assert_called_once()


async def test_get_by_id_success(snippet_doc_repo, snippet_doc):
    result = await snippet_doc_repo.get_by_id(str(snippet_doc.id))
    assert result is not None
    assert result.id == snippet_doc.id


async def test_get_by_id_not_found(snippet_doc_repo):
    result = await snippet_doc_repo.get_by_id(str(PydanticObjectId()))
    assert result is None


async def test_get_by_id_pymongo_error(mocker, snippet_doc_repo):
    mock = mocker.patch(
        "src.adapters.mongo.repo.SnippetDocument.get",
        side_effect=PyMongoError,
    )
    with pytest.raises(PyMongoError):
        await snippet_doc_repo.get_by_id(str(PydanticObjectId()))
    mock.assert_called_once()


# --- get_by_ids ---
async def test_get_by_ids_success(snippet_doc_repo, snippet_doc):
    ids = [str(snippet_doc.id)]
    results = await snippet_doc_repo.get_by_ids(ids)
    assert len(results) == 1
    assert results[0].id == snippet_doc.id


async def test_get_by_ids_empty(snippet_doc_repo):
    results = await snippet_doc_repo.get_by_ids([])
    assert results == []


async def test_get_by_ids_pymongo_error(mocker, snippet_doc_repo):
    mock = mocker.patch(
        "src.adapters.mongo.repo.SnippetDocument.find",
        side_effect=PyMongoError,
    )
    with pytest.raises(PyMongoError):
        await snippet_doc_repo.get_by_ids([str(PydanticObjectId())])
    mock.assert_called_once()


async def test_update_success(snippet_doc_repo, snippet_doc):
    updated = await snippet_doc_repo.update(
        str(snippet_doc.id), content="New content"
    )
    assert updated is not None
    assert updated.content == "New content"


async def test_update_not_found(snippet_doc_repo):
    result = await snippet_doc_repo.update(
        str(PydanticObjectId()), content="x"
    )
    assert result is None


async def test_update_validation_error(snippet_doc_repo, snippet_doc):
    with pytest.raises(ValueError):
        await snippet_doc_repo.update(str(snippet_doc.id), content=1)


async def test_update_pymongo_error(mocker, snippet_doc_repo, snippet_doc):
    mock = mocker.patch(
        "src.adapters.mongo.repo.SnippetDocument.save",
        side_effect=PyMongoError,
    )
    with pytest.raises(PyMongoError):
        await snippet_doc_repo.update(str(snippet_doc.id), content="boom")
    mock.assert_called_once()


async def test_delete_success(snippet_doc_repo, snippet_doc):
    await snippet_doc_repo.delete(str(snippet_doc.id))
    result = await snippet_doc_repo.get_by_id(str(snippet_doc.id))
    assert result is None


async def test_delete_not_found(snippet_doc_repo):
    await snippet_doc_repo.delete(str(PydanticObjectId()))


async def test_delete_pymongo_error(mocker, snippet_doc_repo, snippet_doc):
    mock = mocker.patch(
        "src.adapters.mongo.repo.SnippetDocument.delete",
        side_effect=PyMongoError,
    )
    with pytest.raises(PyMongoError):
        await snippet_doc_repo.delete(str(snippet_doc.id))
    mock.assert_called_once()


async def test_delete_document_success(snippet_doc_repo, snippet_doc):
    await snippet_doc_repo.delete_document(snippet_doc)
    result = await snippet_doc_repo.get_by_id(str(snippet_doc.id))
    assert result is None


async def test_delete_document_pymongo_error(
    mocker, snippet_doc_repo, snippet_doc
):
    mock = mocker.patch(
        "src.adapters.mongo.repo.SnippetDocument.delete",
        side_effect=PyMongoError,
    )
    with pytest.raises(PyMongoError):
        await snippet_doc_repo.delete_document(snippet_doc)
    mock.assert_called_once()
