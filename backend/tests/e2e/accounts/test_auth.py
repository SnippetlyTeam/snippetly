from .helpers import extract_refresh_token_from_set_cookie
from .routes import login_url, refresh_url, logout_url, revoke_all_tokens_url


async def test_login_success_with_email(db, user_factory, client):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    response = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data and isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"

    set_cookie_header = response.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie_header


async def test_login_success_with_username(db, user_factory, client):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    response = await client.post(
        login_url,
        json={"login": user.username, "password": "Test1234!"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_user_not_found(client):
    response = await client.post(
        login_url,
        json={"login": "unknown_user", "password": "SomePass123!"},
    )
    assert response.status_code == 404


async def test_login_invalid_password(db, user_factory, client):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    response = await client.post(
        login_url,
        json={"login": user.email, "password": "WrongPass999!"},
    )
    assert response.status_code == 401


async def test_login_user_not_active(db, user_factory, client):
    user = await user_factory.create(db, is_active=False)
    await db.commit()

    response = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert response.status_code == 403


async def test_refresh_success_via_cookie_after_login(
    db, user_factory, client
):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    login_resp = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert login_resp.status_code == 200
    refresh_cookie = login_resp.headers.get("set-cookie", "")
    token = extract_refresh_token_from_set_cookie(refresh_cookie)
    assert token

    refresh_resp = await client.post(
        refresh_url, cookies={"refresh_token": token}
    )

    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data and isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"


async def test_refresh_missing_cookie(client):
    response = await client.post(refresh_url)
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token not found in cookies"


async def test_refresh_invalid_token(client):
    response = await client.post(
        refresh_url,
        cookies={"refresh_token": "invalid.refresh.token"},
    )
    assert response.status_code == 401


async def test_revoke_all_tokens_success(db, user_factory, client):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    login_resp = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]

    resp = await client.post(
        revoke_all_tokens_url,
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert resp.status_code == 200
    assert (
        resp.json()["message"] == "Logged out from every session successfully"
    )


async def test_revoke_all_tokens_unauthorized(client):
    resp = await client.post(revoke_all_tokens_url)
    assert resp.status_code == 401


async def test_logout_success_clears_cookie(db, user_factory, client):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    login_resp = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert login_resp.status_code == 200

    set_cookie_header = login_resp.headers.get("set-cookie", "")
    refresh_token = extract_refresh_token_from_set_cookie(set_cookie_header)
    assert refresh_token

    access_token = login_resp.json()["access_token"]

    resp = await client.post(
        logout_url,
        headers={"Authorization": f"Bearer {access_token}"},
        cookies={"refresh_token": refresh_token},
    )

    assert resp.status_code == 200
    assert resp.json()["message"] == "Logged out successfully"

    clear_cookie_header = resp.headers.get("set-cookie", "")
    assert "refresh_token=" in clear_cookie_header
    assert "Max-Age=0" in clear_cookie_header


async def test_logout_unauthorized(client):
    resp = await client.post(logout_url)
    assert resp.status_code == 401
