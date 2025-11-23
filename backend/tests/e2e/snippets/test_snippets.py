from datetime import datetime, timezone, timedelta

from src.adapters.postgres.models import LanguageEnum
from .routes import snippet_url


async def test_create_snippet_success(auth_client, db, snippet_model_repo):
    client, user = auth_client

    data = {
        "title": "New Snippet",
        "description": "Simple test snippet",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('Hello, World!')",
        "is_private": False,
        "tags": ["test", "example"],
    }

    response = await client.post(snippet_url, json=data)
    assert response.status_code == 201

    body = response.json()
    assert body["title"] == data["title"]
    assert body["language"] == data["language"]
    assert body["username"] == user.username

    snippet = await snippet_model_repo.get_by_title(data["title"], user.id)
    assert snippet is not None


async def test_create_snippet_unauthorized(client):
    data = {
        "title": "Unauthorized Snippet",
        "description": "Should fail",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('No auth')",
        "is_private": False,
    }

    response = await client.post(snippet_url, json=data)
    assert response.status_code == 401
    assert "detail" in response.json()


async def test_create_snippet_duplicate_title(auth_client, db):
    client, user = auth_client

    data = {
        "title": "Duplicate Snippet",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('dup')",
        "is_private": False,
    }

    response1 = await client.post(snippet_url, json=data)
    assert response1.status_code == 201

    response2 = await client.post(snippet_url, json=data)
    assert response2.status_code == 409


async def test_create_snippet_validation_error(auth_client):
    client, _ = auth_client

    invalid_data = {
        "title": "",
        "language": "INVALID_LANG",
        "content": "",
    }

    response = await client.post(snippet_url, json=invalid_data)
    assert response.status_code == 422


async def test_get_all_snippets_basic(auth_client, setup_snippets):
    client, _ = auth_client

    response = await client.get(snippet_url)
    assert response.status_code == 200

    body = response.json()
    assert body["page"] == 1
    assert body["per_page"] == 10
    assert body["total_items"] == 3
    assert body["total_pages"] == 1

    items = body["snippets"]
    assert len(items) == 3
    assert all(item["is_private"] is False for item in items)


async def test_get_all_snippets_filter_language(auth_client, setup_snippets):
    client, _ = auth_client

    response = await client.get(
        snippet_url, params={"language": LanguageEnum.PYTHON.value}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_items"] == 2
    assert all(
        item["language"] == LanguageEnum.PYTHON for item in data["snippets"]
    ) or all(
        item["language"] == LanguageEnum.PYTHON.value
        for item in data["snippets"]
    )


async def test_get_all_snippets_filter_username(auth_client, setup_snippets):
    client, _ = auth_client
    user1 = setup_snippets["user1"]

    response = await client.get(
        snippet_url, params={"username": user1.username}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_items"] == 2
    assert len(data["snippets"]) == 2


async def test_get_all_snippets_filter_tags(auth_client, setup_snippets):
    client, _ = auth_client

    response = await client.get(snippet_url, params={"tags": "test"})
    assert response.status_code == 200
    data = response.json()

    assert data["total_items"] == 2
    assert len(data["snippets"]) == 2
    assert all("test" in item["tags"] for item in data["snippets"])


async def test_get_all_snippets_filter_created_before(
    auth_client, setup_snippets
):
    client, _ = auth_client

    created_before = (
        (datetime.now(timezone.utc) - timedelta(days=3)).date().isoformat()
    )

    response = await client.get(
        snippet_url, params={"created_before": created_before}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["total_items"] == 1
    assert len(data["snippets"]) == 1


async def test_get_all_snippets_pagination(auth_client, setup_snippets):
    client, _ = auth_client

    resp1 = await client.get(snippet_url, params={"per_page": 2, "page": 1})
    assert resp1.status_code == 200
    d1 = resp1.json()
    assert d1["per_page"] == 2
    assert d1["page"] == 1
    assert d1["total_items"] == 3
    assert d1["total_pages"] == 2
    assert len(d1["snippets"]) == 2
    assert d1["next_page"]
    assert d1["prev_page"] is None

    resp2 = await client.get(snippet_url, params={"per_page": 2, "page": 2})
    assert resp2.status_code == 200
    d2 = resp2.json()
    assert d2["page"] == 2
    assert len(d2["snippets"]) == 1
    assert d2["prev_page"]


async def test_get_snippet_public_success(auth_client, setup_snippets):
    client, _ = auth_client
    public_snippet = setup_snippets["u1_public_py"]

    response = await client.get(f"{snippet_url}{public_snippet.uuid}")
    assert response.status_code == 200
    data = response.json()

    assert data["uuid"] == str(public_snippet.uuid)
    assert data["title"] == public_snippet.title
    assert isinstance(data["language"], str)
    assert "username" in data
    assert "created_at" in data and "updated_at" in data
    assert data["is_private"] is False
    assert isinstance(data.get("tags", []), list)


async def test_get_snippet_private_other_user_forbidden(
    auth_client, setup_snippets
):
    client, _ = auth_client
    private_snippet = setup_snippets["u1_private_py"]

    response = await client.get(f"{snippet_url}{private_snippet.uuid}")
    assert response.status_code == 403
    body = response.json()
    assert "detail" in body


async def test_get_snippet_private_owner_success(auth_client):
    client, _ = auth_client
    create_payload = {
        "title": "My Private",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('secret')",
        "is_private": True,
        "tags": ["secret"],
    }
    create_resp = await client.post(snippet_url, json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()

    get_resp = await client.get(f"{snippet_url}{created['uuid']}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["uuid"] == created["uuid"]
    assert data["is_private"] is True
    assert data["title"] == create_payload["title"]


async def test_get_snippet_not_found(auth_client):
    client, _ = auth_client
    from uuid import uuid4

    nonexistent_uuid = uuid4()
    response = await client.get(f"{snippet_url}{nonexistent_uuid}")
    assert response.status_code == 404
    body = response.json()
    assert "detail" in body


async def test_update_snippet_owner_partial_update_success(auth_client):
    client, _ = auth_client

    create_payload = {
        "title": "Patch Me",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('v1')",
        "is_private": False,
        "description": "desc v1",
        "tags": ["FirstTag", "second tag"],
    }
    create_resp = await client.post(snippet_url, json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()

    patch_payload = {
        "title": "Patched Title",
        "tags": ["New_Tag", " Another "],
    }
    patch_resp = await client.patch(
        f"{snippet_url}{created['uuid']}", json=patch_payload
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()

    assert data["uuid"] == created["uuid"]
    assert data["title"] == patch_payload["title"]
    assert sorted(data.get("tags", [])) == sorted(["new_tag", "another"])
    assert isinstance(data["language"], str)
    assert data["content"] == create_payload["content"]
    assert data["description"] == create_payload["description"]
    assert data["is_private"] is False

    get_resp = await client.get(f"{snippet_url}{created['uuid']}")
    assert get_resp.status_code == 200
    got = get_resp.json()
    assert got["title"] == patch_payload["title"]
    assert sorted(got.get("tags", [])) == sorted(["new_tag", "another"])


async def test_update_snippet_owner_full_update_success(auth_client):
    client, _ = auth_client

    create_payload = {
        "title": "Full Patch",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('old')",
        "is_private": False,
        "description": "old desc",
        "tags": ["old", "t1"],
    }
    c = await client.post(snippet_url, json=create_payload)
    assert c.status_code == 201
    created = c.json()

    update_payload = {
        "title": "Full Patched",
        "language": LanguageEnum.JAVASCRIPT.value,
        "is_private": True,
        "content": "console.log('new')",
        "description": "new desc",
        "tags": ["JS", "new tag"],
    }

    u = await client.patch(
        f"{snippet_url}{created['uuid']}", json=update_payload
    )
    assert u.status_code == 200
    updated = u.json()

    assert updated["uuid"] == created["uuid"]
    assert updated["title"] == update_payload["title"]
    assert isinstance(updated["language"], str)
    assert updated["language"] in (
        LanguageEnum.JAVASCRIPT.value,
        str(LanguageEnum.JAVASCRIPT),
    )
    assert updated["is_private"] is True
    assert updated["content"] == update_payload["content"]
    assert updated["description"] == update_payload["description"]
    assert sorted(updated.get("tags", [])) == sorted(
        ["js", "newtag"]
    ) or sorted(updated.get("tags", [])) == sorted(["js", "new_tag"])

    g = await client.get(f"{snippet_url}{created['uuid']}")
    assert g.status_code == 200
    gdata = g.json()
    assert gdata["title"] == update_payload["title"]
    assert gdata["is_private"] is True


async def test_update_snippet_other_user_forbidden(
    auth_client, setup_snippets
):
    client, _ = auth_client
    target = setup_snippets["u1_public_py"]

    resp = await client.patch(
        f"{snippet_url}{target.uuid}", json={"title": "nope"}
    )
    assert resp.status_code == 403
    body = resp.json()
    assert "detail" in body


async def test_update_snippet_not_found(auth_client):
    client, _ = auth_client
    from uuid import uuid4

    random_uuid = uuid4()
    resp = await client.patch(
        f"{snippet_url}{random_uuid}", json={"title": "x" * 5}
    )
    assert resp.status_code == 404
    body = resp.json()
    assert "detail" in body


async def test_update_snippet_validation_error(auth_client):
    client, _ = auth_client

    create_payload = {
        "title": "Valid Before",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('ok')",
        "is_private": False,
        "tags": ["ok"],
    }
    create_resp = await client.post(snippet_url, json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()

    invalid_patch = {"language": "INVALID_LANG", "title": "ab"}
    resp = await client.patch(
        f"{snippet_url}{created['uuid']}", json=invalid_patch
    )
    assert resp.status_code == 422


async def test_delete_snippet_owner_public_success(auth_client):
    client, _ = auth_client

    create_payload = {
        "title": "Delete Public",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('bye')",
        "is_private": False,
        "tags": ["cleanup"],
    }
    c = await client.post(snippet_url, json=create_payload)
    assert c.status_code == 201
    created = c.json()

    d = await client.delete(f"{snippet_url}{created['uuid']}")
    assert d.status_code == 200
    body = d.json()
    assert body["message"] == "Snippet has been deleted successfully"

    g = await client.get(f"{snippet_url}{created['uuid']}")
    assert g.status_code == 404


async def test_delete_snippet_owner_private_success(auth_client):
    client, _ = auth_client

    create_payload = {
        "title": "Delete Private",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('secret bye')",
        "is_private": True,
        "tags": ["secret"],
    }
    c = await client.post(snippet_url, json=create_payload)
    assert c.status_code == 201
    created = c.json()

    d = await client.delete(f"{snippet_url}{created['uuid']}")
    assert d.status_code == 200
    body = d.json()
    assert body["message"] == "Snippet has been deleted successfully"

    g = await client.get(f"{snippet_url}{created['uuid']}")
    assert g.status_code == 404


async def test_delete_snippet_other_user_forbidden(
    auth_client, setup_snippets
):
    client, _ = auth_client
    foreign_snippet = setup_snippets["u1_public_py"]

    resp = await client.delete(f"{snippet_url}{foreign_snippet.uuid}")
    assert resp.status_code == 403
    data = resp.json()
    assert "detail" in data


async def test_delete_snippet_nonexistent_returns_success_message(auth_client):
    client, _ = auth_client
    from uuid import uuid4

    random_uuid = uuid4()
    resp = await client.delete(f"{snippet_url}{random_uuid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Snippet has been deleted successfully"
