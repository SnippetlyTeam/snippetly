from tests.utils.user import create_user_data
from .helpers import extract_refresh_token_from_set_cookie
from .routes import (
    register_url,
    activate_url,
    login_url,
    refresh_url,
    logout_url,
    revoke_all_tokens_url,
    profile_url,
    avatar_url,
)


async def test_register_activate_login(client, email_sender_mock, faker):
    user_data = create_user_data(faker)
    response = await client.post(register_url, json=user_data)

    assert response.status_code == 201

    sent_emails = email_sender_mock.get_sent_emails(user_data["email"])
    token = sent_emails[0]["token"]

    activate_response = await client.post(
        activate_url, json={"activation_token": token}
    )
    assert activate_response.status_code == 200

    login_response = await client.post(
        login_url,
        json={"login": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200


async def test_login_refresh_logout_flow(db, user_factory, client):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    login_resp = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]
    set_cookie_header = login_resp.headers.get("set-cookie", "")
    refresh_token = extract_refresh_token_from_set_cookie(set_cookie_header)
    assert refresh_token

    refresh_ok = await client.post(
        refresh_url,
        cookies={"refresh_token": refresh_token},
    )
    assert refresh_ok.status_code == 200

    logout_resp = await client.post(
        logout_url,
        headers={"Authorization": f"Bearer {access_token}"},
        cookies={"refresh_token": refresh_token},
    )
    assert logout_resp.status_code == 200

    refresh_after_logout = await client.post(
        refresh_url,
        cookies={"refresh_token": refresh_token},
    )
    assert refresh_after_logout.status_code == 401


async def test_revoke_all_tokens_invalidates_all_sessions(
    db, user_factory, client
):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    login_a = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert login_a.status_code == 200
    access_token_a = login_a.json()["access_token"]
    rt_cookie_a = extract_refresh_token_from_set_cookie(
        login_a.headers.get("set-cookie", "")
    )
    assert rt_cookie_a

    login_b = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert login_b.status_code == 200
    rt_cookie_b = extract_refresh_token_from_set_cookie(
        login_b.headers.get("set-cookie", "")
    )
    assert rt_cookie_b

    revoke_resp = await client.post(
        revoke_all_tokens_url,
        headers={"Authorization": f"Bearer {access_token_a}"},
    )
    assert revoke_resp.status_code == 200

    refresh_a = await client.post(
        refresh_url,
        cookies={"refresh_token": rt_cookie_a},
    )
    refresh_b = await client.post(
        refresh_url,
        cookies={"refresh_token": rt_cookie_b},
    )

    assert refresh_a.status_code == 401
    assert refresh_b.status_code == 401


async def test_profile_e2e_flow(auth_client, avatar_file):
    client, user = auth_client

    profile_resp = await client.get(profile_url)
    assert profile_resp.status_code == 200
    profile_data = profile_resp.json()
    assert profile_data["username"] == user.username
    assert "email" not in profile_data

    profile_specific = await client.get(f"{profile_url}{user.username}")
    assert profile_specific.status_code == 200
    data = profile_specific.json()
    assert data["username"] == user.username

    update_data = {
        "first_name": "John",
        "last_name": "Doe",
        "info": "QA engineer",
    }
    patch_resp = await client.patch(profile_url, json=update_data)
    assert patch_resp.status_code == 200
    patched = patch_resp.json()
    assert patched["first_name"] == "John"
    assert patched["info"] == "QA engineer"

    avatar_resp = await client.post(
        avatar_url,
        files={"avatar": avatar_file},
    )
    assert avatar_resp.status_code == 200
    assert avatar_resp.json()["message"] == "Profile picture updated"

    delete_resp = await client.delete(avatar_url)
    assert delete_resp.status_code == 200
    assert (
        delete_resp.json()["message"]
        == "Profile avatar has been deleted successfully"
    )


async def test_profile_not_found_returns_404(auth_client):
    client, _ = auth_client
    resp = await client.get(f"{profile_url}/nonexistent_user")
    assert resp.status_code == 404
