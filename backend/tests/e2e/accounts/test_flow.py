from tests.utils.user import create_user_data
from .routes import (
    register_url,
    activate_url,
    login_url,
    refresh_url,
    logout_url,
    revoke_all_tokens_url,
)


def _extract_refresh_token_from_set_cookie(
    set_cookie_header: str,
) -> str | None:
    prefix = "refresh_token="
    if prefix not in set_cookie_header:
        return None
    after = set_cookie_header.split(prefix, 1)[1]
    return after.split(";", 1)[0]


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
    refresh_token = _extract_refresh_token_from_set_cookie(set_cookie_header)
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
    rt_cookie_a = _extract_refresh_token_from_set_cookie(
        login_a.headers.get("set-cookie", "")
    )
    assert rt_cookie_a

    login_b = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert login_b.status_code == 200
    rt_cookie_b = _extract_refresh_token_from_set_cookie(
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
