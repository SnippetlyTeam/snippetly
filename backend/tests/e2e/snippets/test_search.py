from urllib.parse import quote

from src.adapters.postgres.models import LanguageEnum
from .routes import search_url, snippet_url


async def test_search_unauthorized(client, setup_snippets):
    target_title = setup_snippets["u1_public_py"].title
    resp = await client.get(f"{search_url}{quote(target_title)}")
    assert resp.status_code == 401
    assert "detail" in resp.json()


async def test_search_basic_http_success(auth_client, setup_snippets):
    client, _ = auth_client
    target_snippet = setup_snippets["u1_public_js"]

    resp = await client.get(f"{search_url}{quote(target_snippet.title)}")
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data.get("results"), list)
    assert len(data["results"]) <= 20

    uuids = {item["uuid"] for item in data["results"]}
    assert str(target_snippet.uuid) in uuids

    for item in data["results"]:
        assert {"uuid", "title", "language"}.issubset(item.keys())


async def test_search_case_insensitive_and_url_encoding(auth_client):
    client, user = auth_client

    title = "My Fancy Snippet v1"
    payload = {
        "title": title,
        "description": "E2E search encoding test",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('encoding')",
        "is_private": False,
        "tags": ["search", "e2e"],
    }
    create_resp = await client.post(snippet_url, json=payload)
    assert create_resp.status_code == 201

    query = title.lower()
    search_resp = await client.get(f"{search_url}{quote(query)}")
    assert search_resp.status_code == 200
    items = search_resp.json()["results"]
    assert any(item["title"].lower() == query for item in items)


async def test_search_limit_enforced(auth_client):
    client, user = auth_client

    prefix = "Batch Item"
    for i in range(25):
        payload = {
            "title": f"{prefix} {i}",
            "language": LanguageEnum.PYTHON.value,
            "content": f"print({i})",
            "is_private": False,
        }
        resp = await client.post(snippet_url, json=payload)
        assert resp.status_code == 201

    resp = await client.get(f"{search_url}{quote(prefix)}")
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert len(results) <= 20
    assert all(prefix.lower() in item["title"].lower() for item in results)


async def test_search_excludes_others_private(auth_client, setup_snippets):
    client, _ = auth_client
    other_private = setup_snippets["u2_private_js"]

    resp = await client.get(f"{search_url}{quote(other_private.title)}")
    assert resp.status_code == 200
    items = resp.json()["results"]
    assert all(item["uuid"] != str(other_private.uuid) for item in items)
