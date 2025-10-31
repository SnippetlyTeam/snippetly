from .routes import (
    reset_password_request_url,
    reset_password_complete_url,
    change_password_url,
    login_url,
)

message_request = (
    "If an account with that email exists, "
    "we've sent password reset instructions. Please check your inbox"
)


async def test_reset_password_request_existing_email_sends_email(
    db, user_factory, client, email_sender_mock
):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    resp = await client.post(
        reset_password_request_url,
        json={"email": user.email},
    )

    assert resp.status_code == 202
    assert resp.json()["message"] == message_request

    sent = email_sender_mock.get_sent_emails(user.email)
    assert len(sent) == 1
    assert sent[0]["type"] == "password_reset"
    assert "token" in sent[0] and isinstance(sent[0]["token"], str)


async def test_reset_password_request_nonexistent_email_noop(
    client, faker, email_sender_mock
):
    email = faker.unique.email()

    resp = await client.post(
        reset_password_request_url,
        json={"email": email},
    )

    assert resp.status_code == 202
    assert resp.json()["message"] == message_request

    sent = email_sender_mock.get_sent_emails(email)
    assert len(sent) == 0


async def test_reset_password_complete_success(db, user_factory, client):
    user, token = await user_factory.create_with_reset_token(
        db, "token_rst_123"
    )
    await db.commit()

    new_password = "NewPass123!"

    resp = await client.post(
        reset_password_complete_url,
        json={
            "email": user.email,
            "password": new_password,
            "password_reset_token": token,
        },
    )

    assert resp.status_code == 200
    assert resp.json()["message"] == "Password has been successfully changed"

    login_resp = await client.post(
        login_url,
        json={"login": user.email, "password": new_password},
    )
    assert login_resp.status_code == 200

    bad_login = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert bad_login.status_code == 401


async def test_change_password_success(db, user_factory, client):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    login_resp = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]

    new_password = "BrandNew1!"

    resp = await client.post(
        change_password_url,
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "old_password": "Test1234!",
            "new_password": new_password,
        },
    )

    assert resp.status_code == 200
    assert resp.json()["message"] == "Password has been successfully changed"

    good_login = await client.post(
        login_url,
        json={"login": user.email, "password": new_password},
    )
    assert good_login.status_code == 200

    bad_login = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert bad_login.status_code == 401


async def test_change_password_invalid_old_password(db, user_factory, client):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    login_resp = await client.post(
        login_url,
        json={"login": user.email, "password": "Test1234!"},
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]

    resp = await client.post(
        change_password_url,
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "old_password": "WrongPass123!",
            "new_password": "AnotherNew1!",
        },
    )

    assert resp.status_code == 403
