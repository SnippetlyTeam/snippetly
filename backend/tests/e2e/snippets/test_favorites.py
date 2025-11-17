from uuid import uuid4

import pytest

from src.adapters.postgres.models import LanguageEnum
from src.core.exceptions import FavoritesAlreadyError
from .routes import favorites_url


async def test_add_favorite_success(
    auth_client, setup_snippets, favorites_repo, db
):
    client, user = auth_client

    target_snippet = setup_snippets["u1_public_py"]

    resp = await client.post(
        favorites_url, json={"uuid": str(target_snippet.uuid)}
    )
    assert resp.status_code == 201

    body = resp.json()
    assert body["message"] == "Snippet added to favorites"

    with pytest.raises(FavoritesAlreadyError):
        await favorites_repo.add_to_favorites(user, target_snippet.uuid)
    await db.rollback()


async def test_add_favorite_unauthorized(client, setup_snippets):
    target_snippet = setup_snippets["u1_public_py"]

    resp = await client.post(
        favorites_url, json={"uuid": str(target_snippet.uuid)}
    )
    assert resp.status_code == 401
    assert "detail" in resp.json()


async def test_add_favorite_not_found(auth_client):
    client, _ = auth_client

    resp = await client.post(favorites_url, json={"uuid": str(uuid4())})
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Snippet with this UUID was not found"


async def test_add_favorite_conflict(auth_client, setup_snippets):
    client, _ = auth_client
    target_snippet = setup_snippets["u1_public_py"]

    resp1 = await client.post(
        favorites_url, json={"uuid": str(target_snippet.uuid)}
    )
    assert resp1.status_code == 201

    resp2 = await client.post(
        favorites_url, json={"uuid": str(target_snippet.uuid)}
    )
    assert resp2.status_code == 409
    assert (
        resp2.json().get("detail")
        == "Snippet with this UUID already favorited"
    )


async def _add_favorites_for(auth_client, setup_snippets):
    client, user = auth_client
    targets = [
        setup_snippets["u1_public_py"],
        setup_snippets["u1_public_js"],
        setup_snippets["u2_public_py"],
    ]
    for sn in targets:
        resp = await client.post(favorites_url, json={"uuid": str(sn.uuid)})
        assert resp.status_code in (201, 409)
    return targets


async def test_get_favorites_basic(auth_client, setup_snippets):
    client, _ = auth_client
    targets = await _add_favorites_for(auth_client, setup_snippets)

    resp = await client.get(favorites_url)
    assert resp.status_code == 200

    body = resp.json()
    assert body["page"] == 1
    assert body["per_page"] == 10
    assert body["total_items"] == len(targets)
    assert body["total_pages"] == 1

    items = body["snippets"]
    assert len(items) == len(targets)
    target_uuids = {str(t.uuid) for t in targets}
    assert target_uuids.issuperset({it["uuid"] for it in items})


async def test_get_favorites_unauthorized(client):
    resp = await client.get(favorites_url)
    assert resp.status_code == 401
    assert "detail" in resp.json()


async def test_get_favorites_filter_language(auth_client, setup_snippets):
    client, _ = auth_client
    await _add_favorites_for(auth_client, setup_snippets)

    resp = await client.get(
        favorites_url, params={"language": LanguageEnum.PYTHON.value}
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_items"] >= 1
    assert all(
        it["language"] == LanguageEnum.PYTHON
        or it["language"] == LanguageEnum.PYTHON.value
        for it in data["snippets"]
    )


async def test_get_favorites_filter_tag(auth_client, setup_snippets):
    client, _ = auth_client
    await _add_favorites_for(auth_client, setup_snippets)

    resp = await client.get(favorites_url, params=[("tags", "test")])
    assert resp.status_code == 200
    data = resp.json()

    assert (
        all("test" in it.get("tags", []) for it in data["snippets"])
        or data["total_items"] == 0
    )


async def test_get_favorites_filter_username(auth_client, setup_snippets):
    client, _ = auth_client
    await _add_favorites_for(auth_client, setup_snippets)

    owner_username = setup_snippets["user2"].username
    resp = await client.get(favorites_url, params={"username": owner_username})
    assert resp.status_code == 200
    data = resp.json()
    assert (
        all(it["username"] == owner_username for it in data["snippets"])
        or data["total_items"] == 0
    )


async def test_get_favorites_sorting_title(auth_client, setup_snippets):
    client, _ = auth_client
    await _add_favorites_for(auth_client, setup_snippets)

    resp = await client.get(favorites_url, params={"sort_by": "title"})
    assert resp.status_code == 200
    titles = [it["title"] for it in resp.json()["snippets"]]
    assert titles == sorted(titles, key=str.lower)


async def test_get_favorites_pagination(auth_client, setup_snippets):
    client, _ = auth_client
    await _add_favorites_for(auth_client, setup_snippets)

    resp1 = await client.get(favorites_url, params={"per_page": 2, "page": 1})
    resp2 = await client.get(favorites_url, params={"per_page": 2, "page": 2})

    assert resp1.status_code == 200 and resp2.status_code == 200
    b1, b2 = resp1.json(), resp2.json()

    assert b1["total_items"] in (2, 3)
    assert b1["per_page"] == 2
    assert b2["per_page"] == 2

    ids1 = {it["uuid"] for it in b1["snippets"]}
    ids2 = {it["uuid"] for it in b2["snippets"]}
    assert not ids1.intersection(ids2)


async def test_get_favorites_empty(auth_client):
    client, _ = auth_client
    resp = await client.get(favorites_url)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_items"] == 0
    assert data["snippets"] == []


async def test_delete_favorite_success(
    auth_client, setup_snippets, favorites_repo, db
):
    client, user = auth_client
    target = setup_snippets["u1_public_py"]

    resp_add = await client.post(
        favorites_url, json={"uuid": str(target.uuid)}
    )
    assert resp_add.status_code in (201, 409)

    resp_del = await client.delete(f"{favorites_url}{target.uuid}")
    assert resp_del.status_code == 200
    assert resp_del.json().get("message") == "Snippet removed from favorites"

    with pytest.raises(FavoritesAlreadyError):
        await favorites_repo.remove_from_favorites(user, target.uuid)
    await db.rollback()


async def test_delete_favorite_idempotent(auth_client, setup_snippets):
    client, _ = auth_client
    target = setup_snippets["u1_public_js"]

    resp1 = await client.delete(f"{favorites_url}{target.uuid}")
    resp2 = await client.delete(f"{favorites_url}{target.uuid}")

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp1.json().get("message") == "Snippet removed from favorites"
    assert resp2.json().get("message") == "Snippet removed from favorites"


async def test_delete_favorite_not_found(auth_client):
    client, _ = auth_client
    resp = await client.delete(f"{favorites_url}{uuid4()}")
    assert resp.status_code == 404
    assert resp.json().get("detail") == "Snippet with this UUID was not found"


async def test_delete_favorite_unauthorized(client, setup_snippets):
    target = setup_snippets["u2_public_py"]
    resp = await client.delete(f"{favorites_url}{target.uuid}")
    assert resp.status_code == 401
    assert "detail" in resp.json()
