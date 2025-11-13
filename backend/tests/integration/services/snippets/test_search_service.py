import json


async def test_search_by_title_returns_correct_snippets(
    search_service, setup_snippets, redis_client
):
    user1 = setup_snippets["user1"]
    u1_pub_py = setup_snippets["u1_public_py"]

    await redis_client.flushall()

    response = await search_service.search_by_title(
        u1_pub_py.title, user1.id, limit=10
    )

    assert isinstance(response.results, list)
    assert any(s.uuid == u1_pub_py.uuid for s in response.results)
    u1_priv_py = setup_snippets["u1_private_py"]
    response_private = await search_service.search_by_title(
        u1_priv_py.title, user1.id, limit=10
    )
    assert any(s.uuid == u1_priv_py.uuid for s in response_private.results)


async def test_search_by_title_respects_privacy(
    search_service, setup_snippets
):
    user1 = setup_snippets["user1"]
    u2_priv_js = setup_snippets["u2_private_js"]

    response = await search_service.search_by_title(
        u2_priv_js.title, user1.id, limit=10
    )
    assert all(s.uuid != u2_priv_js.uuid for s in response.results)


async def test_search_by_title_uses_cache(
    search_service, setup_snippets, redis_client
):
    user1 = setup_snippets["user1"]
    u1_pub_py = setup_snippets["u1_public_py"]

    await redis_client.flushall()

    await search_service.search_by_title(u1_pub_py.title, user1.id, limit=10)

    cache_key = f"search:{user1.id}:{u1_pub_py.title.lower()}"
    cached = await redis_client.get(cache_key)
    assert cached is not None

    cached_data = json.loads(cached)
    assert any(
        item["uuid"] == str(u1_pub_py.uuid) for item in cached_data["results"]
    )


async def test_search_by_title_partial_match(search_service, setup_snippets):
    user1 = setup_snippets["user1"]
    u1_pub_py = setup_snippets["u1_public_py"]

    keyword = u1_pub_py.title.split()[0]
    response = await search_service.search_by_title(
        keyword, user1.id, limit=10
    )
    assert any(keyword in s.title for s in response.results)


async def test_search_by_title_limit(search_service, setup_snippets):
    user1 = setup_snippets["user1"]
    u1_pub_py = setup_snippets["u1_public_py"]

    response = await search_service.search_by_title(
        u1_pub_py.title, user1.id, limit=1
    )
    assert len(response.results) == 1
