from src.adapters.postgres.models import LanguageEnum
from .routes import snippet_url


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
