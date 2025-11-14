from src.adapters.postgres.models import LanguageEnum
from .routes import snippet_url, favorites_url, search_url


async def test_full_crud_flow(auth_client):
    client, _ = auth_client

    create_payload = {
        "title": "Flow One",
        "language": LanguageEnum.PYTHON.value,
        "content": "print('v1')",
        "description": "d1",
        "is_private": False,
        "tags": ["One_Tag", " another"],
    }
    c = await client.post(snippet_url, json=create_payload)
    assert c.status_code == 201
    created = c.json()
    uuid = created["uuid"]

    g1 = await client.get(f"{snippet_url}{uuid}")
    assert g1.status_code == 200

    p = await client.patch(
        f"{snippet_url}{uuid}",
        json={"title": "Flow One Updated", "tags": ["tAg_1", " two "]},
    )
    assert p.status_code == 200
    pdata = p.json()
    assert pdata["title"] == "Flow One Updated"
    assert sorted(pdata.get("tags", [])) == sorted(["tag_1", "two"]) or sorted(
        pdata.get("tags", [])
    ) == sorted(["tag_1", "two"])

    g2 = await client.get(f"{snippet_url}{uuid}")
    assert g2.status_code == 200
    g2d = g2.json()
    assert g2d["title"] == "Flow One Updated"

    full = await client.patch(
        f"{snippet_url}{uuid}",
        json={
            "title": "Flow One Final",
            "language": LanguageEnum.JAVASCRIPT.value,
            "is_private": True,
            "content": "console.log('final')",
            "description": "d2",
            "tags": ["JS", "final tag"],
        },
    )
    assert full.status_code == 200
    fdata = full.json()
    assert fdata["title"] == "Flow One Final"
    assert fdata["is_private"] is True
    assert fdata["content"].startswith("console.log")

    lst = await client.get(
        snippet_url,
        params={
            "language": LanguageEnum.JAVASCRIPT.value,
            "visibility": "private",
            "tags": "finaltag",
        },
    )
    assert lst.status_code == 200
    ldata = lst.json()
    assert any(item["uuid"] == uuid for item in ldata["snippets"])

    d = await client.delete(f"{snippet_url}{uuid}")
    assert d.status_code == 200
    g3 = await client.get(f"{snippet_url}{uuid}")
    assert g3.status_code == 404


async def test_permission_flow_two_users(
    db, client, auth_service, user_factory
):
    user_a = await user_factory.create_active(db)
    tokens_a = await auth_service.login_user(user_a.email, "Test1234!")
    client_a = client
    client_a.headers["Authorization"] = f"Bearer {tokens_a['access_token']}"

    c_priv = await client_a.post(
        snippet_url,
        json={
            "title": "Priv A",
            "language": LanguageEnum.PYTHON.value,
            "content": "print('a')",
            "is_private": True,
        },
    )
    assert c_priv.status_code == 201
    priv_uuid = c_priv.json()["uuid"]

    c_pub = await client_a.post(
        snippet_url,
        json={
            "title": "Pub A",
            "language": LanguageEnum.PYTHON.value,
            "content": "print('a2')",
            "is_private": False,
        },
    )
    assert c_pub.status_code == 201
    pub_uuid = c_pub.json()["uuid"]

    user_b = await user_factory.create_active(db)
    tokens_b = await auth_service.login_user(user_b.email, "Test1234!")
    client_b = client
    client_b.headers["Authorization"] = f"Bearer {tokens_b['access_token']}"

    assert (await client_b.get(f"{snippet_url}{pub_uuid}")).status_code == 200
    assert (await client_b.get(f"{snippet_url}{priv_uuid}")).status_code == 403

    assert (
        await client_b.patch(f"{snippet_url}{pub_uuid}", json={"title": "xxx"})
    ).status_code == 403
    assert (
        await client_b.delete(f"{snippet_url}{pub_uuid}")
    ).status_code == 403

    client_a.headers["Authorization"] = f"Bearer {tokens_a['access_token']}"
    assert (
        await client_a.delete(f"{snippet_url}{priv_uuid}")
    ).status_code == 200


async def test_visibility_and_pagination_flow(auth_client, setup_snippets):
    client, user = auth_client

    base = await client.get(snippet_url)
    assert base.status_code == 200
    b = base.json()
    assert b["page"] == 1 and b["per_page"] > 0
    assert b["total_items"] >= 3

    pub = await client.get(snippet_url, params={"visibility": "public"})
    assert pub.status_code == 200
    pdata = pub.json()
    assert all(not it["is_private"] for it in pdata["snippets"])

    priv = await client.get(snippet_url, params={"visibility": "private"})
    assert priv.status_code == 200
    pr = priv.json()
    assert all(it["is_private"] for it in pr["snippets"]) or pr[
        "total_items"
    ] in (0, 1)

    p1 = await client.get(snippet_url, params={"per_page": 2, "page": 1})
    p2 = await client.get(snippet_url, params={"per_page": 2, "page": 2})
    assert p1.status_code == p2.status_code == 200
    d1, d2 = p1.json(), p2.json()
    assert d1["total_pages"] >= 1
    uuids_p1 = {it["uuid"] for it in d1["snippets"]}
    uuids_p2 = {it["uuid"] for it in d2["snippets"]}
    assert not uuids_p1.intersection(uuids_p2)


async def test_favorites_full_flow(auth_client, setup_snippets):
    client, user = auth_client

    targets = [
        setup_snippets["u1_public_py"],
        setup_snippets["u1_public_js"],
        setup_snippets["u2_public_py"],
    ]

    added_uuids = []
    for snippet in targets:
        resp = await client.post(
            favorites_url, json={"uuid": str(snippet.uuid)}
        )
        assert resp.status_code in (201, 409)
        if resp.status_code == 201:
            added_uuids.append(str(snippet.uuid))

    resp = await client.get(favorites_url)
    assert resp.status_code == 200
    favorites_data = resp.json()

    favorite_uuids = {item["uuid"] for item in favorites_data["snippets"]}
    assert all(uuid in favorite_uuids for uuid in added_uuids)

    python_favorites = await client.get(
        favorites_url, params={"language": LanguageEnum.PYTHON.value}
    )
    assert python_favorites.status_code == 200
    python_data = python_favorites.json()

    assert all(
        item["language"] in (LanguageEnum.PYTHON, LanguageEnum.PYTHON.value)
        for item in python_data["snippets"]
    )

    tagged_favorites = await client.get(favorites_url, params={"tags": "test"})
    assert tagged_favorites.status_code == 200

    paginated_favorites = await client.get(
        favorites_url, params={"per_page": 2, "page": 1}
    )
    assert paginated_favorites.status_code == 200
    paginated_data = paginated_favorites.json()

    assert paginated_data["per_page"] == 2
    assert len(paginated_data["snippets"]) <= 2

    target_to_remove = targets[0]
    delete_resp = await client.delete(
        f"{favorites_url}{target_to_remove.uuid}"
    )
    assert delete_resp.status_code == 200

    after_delete_resp = await client.get(favorites_url)
    assert after_delete_resp.status_code == 200
    after_delete_data = after_delete_resp.json()

    remaining_uuids = {item["uuid"] for item in after_delete_data["snippets"]}
    assert str(target_to_remove.uuid) not in remaining_uuids


async def test_favorites_and_search_integration_flow(
    auth_client, setup_snippets
):
    client, user = auth_client

    test_snippets = [
        {
            "title": "Integration Test Python",
            "language": LanguageEnum.PYTHON.value,
            "content": "print('integration')",
            "is_private": False,
            "tags": ["integration", "test"],
        },
        {
            "title": "Integration Test JS",
            "language": LanguageEnum.JAVASCRIPT.value,
            "content": "console.log('integration')",
            "is_private": False,
            "tags": ["integration", "javascript"],
        },
    ]

    created_uuids = []
    for snippet_data in test_snippets:
        resp = await client.post(snippet_url, json=snippet_data)
        assert resp.status_code == 201
        created_uuids.append(resp.json()["uuid"])

    search_resp = await client.get(f"{search_url}Integration")
    assert search_resp.status_code == 200
    search_results = search_resp.json()["results"]

    integration_uuids = {
        item["uuid"]
        for item in search_results
        if "Integration" in item["title"]
    }

    for uuid in integration_uuids:
        fav_resp = await client.post(favorites_url, json={"uuid": uuid})
        assert fav_resp.status_code in (201, 409)

    favorites_resp = await client.get(favorites_url)
    assert favorites_resp.status_code == 200
    favorites_data = favorites_resp.json()

    favorite_uuids = {item["uuid"] for item in favorites_data["snippets"]}
    assert integration_uuids.issubset(favorite_uuids)

    python_favs = await client.get(
        favorites_url,
        params={"language": LanguageEnum.PYTHON.value, "tags": "integration"},
    )
    assert python_favs.status_code == 200
    python_favs_data = python_favs.json()

    python_integration_found = any(
        item["language"] in (LanguageEnum.PYTHON, LanguageEnum.PYTHON.value)
        and "integration" in [tag.lower() for tag in item.get("tags", [])]
        for item in python_favs_data["snippets"]
    )
    assert python_integration_found

    for uuid in created_uuids:
        await client.delete(f"{snippet_url}{uuid}")
    for uuid in integration_uuids:
        await client.delete(f"{favorites_url}{uuid}")


async def test_favorites_pagination_search_flow(auth_client):
    client, user = auth_client

    base_title = "Pagination Test"
    snippets_to_create = 15

    created_uuids = []
    for i in range(snippets_to_create):
        snippet_data = {
            "title": f"{base_title} {i:02d}",
            "language": LanguageEnum.PYTHON.value,
            "content": f"print('pagination {i}')",
            "is_private": False,
            "tags": ["pagination", f"test{i}"],
        }
        resp = await client.post(snippet_url, json=snippet_data)
        assert resp.status_code == 201
        created_uuids.append(resp.json()["uuid"])

    for uuid in created_uuids:
        fav_resp = await client.post(favorites_url, json={"uuid": uuid})
        assert fav_resp.status_code in (201, 409)

    page1_resp = await client.get(
        favorites_url, params={"per_page": 5, "page": 1, "tags": "pagination"}
    )
    assert page1_resp.status_code == 200
    page1_data = page1_resp.json()

    assert page1_data["page"] == 1
    assert page1_data["per_page"] == 5
    assert len(page1_data["snippets"]) == 5

    page2_resp = await client.get(
        favorites_url, params={"per_page": 5, "page": 2, "tags": "pagination"}
    )
    assert page2_resp.status_code == 200
    page2_data = page2_resp.json()

    assert page2_data["page"] == 2
    assert len(page2_data["snippets"]) == 5

    page1_uuids = {item["uuid"] for item in page1_data["snippets"]}
    page2_uuids = {item["uuid"] for item in page2_data["snippets"]}
    assert not page1_uuids.intersection(page2_uuids)

    search_resp = await client.get(f"{search_url}Pagination Test 07")
    assert search_resp.status_code == 200
    search_data = search_resp.json()

    assert len(search_data["results"]) == 1
    searched_uuid = search_data["results"][0]["uuid"]

    all_favorites = await client.get(favorites_url)
    all_favorites_data = all_favorites.json()

    all_favorite_uuids = {
        item["uuid"] for item in all_favorites_data["snippets"]
    }
    assert searched_uuid in all_favorite_uuids

    for uuid in created_uuids:
        await client.delete(f"{snippet_url}{uuid}")
        await client.delete(f"{favorites_url}{uuid}")
