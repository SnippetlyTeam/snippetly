from tests.utils.user import create_user_data
from .routes import register_url


async def test_register_new_user(client, email_sender_mock, faker):
    user_data = create_user_data(faker)
    response = await client.post(register_url, json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]

    sent_emails = email_sender_mock.get_sent_emails(user_data["email"])
    assert len(sent_emails) == 1
    assert sent_emails[0]["type"] == "activation"
    assert "token" in sent_emails[0]


async def test_register_duplicate_email(db, user_factory, client):
    user = await user_factory.create(db)
    await db.commit()

    response = await client.post(
        register_url,
        json={
            "email": user.email,
            "password": "Test123!",
            "username": "newuser",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "This email is taken."


async def test_register_duplicate_username(db, user_factory, client):
    user = await user_factory.create(db)
    await db.commit()

    response = await client.post(
        register_url,
        json={
            "email": "uniq@test.com",
            "password": "Test123!",
            "username": user.username,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "This username is taken."


async def test_register_invalid_email(client, faker):
    response = await client.post(
        register_url,
        json={
            "email": "invalid-email",
            "password": "SecurePass123!",
            "username": faker.unique.user_name(),
        },
    )
    assert response.status_code == 422


async def test_register_weak_password(client, faker):
    response = await client.post(
        register_url,
        json={
            "email": "user@example.com",
            "password": "123",
            "username": faker.unique.user_name(),
        },
    )
    assert response.status_code == 422
