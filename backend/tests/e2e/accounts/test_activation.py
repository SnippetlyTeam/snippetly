from .routes import activate_url, resend_activation_url


async def test_activate_account_success(db, user_factory, client):
    user, token = await user_factory.create_with_activation_token(
        db, "token1234"
    )
    await db.commit()

    response = await client.post(
        activate_url, json={"activation_token": token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Account has been activated successfully"

    await db.refresh(user)
    assert user.is_active is True


async def test_activate_account_invalid_token(client):
    response = await client.post(
        activate_url, json={"activation_token": "invalid_token_12345"}
    )

    assert response.status_code == 404


async def test_activate_account_expired_token(
    db, user_factory, activation_token_repo, client
):
    user = await user_factory.create(db)
    token = await activation_token_repo.create(user.id, "token1234", -1)
    await db.commit()

    response = await client.post(
        activate_url, json={"activation_token": token.token}
    )

    assert response.status_code == 400


message = (
    "If an inactive account exists "
    "for this email, an activation email has been sent."
)


async def test_resend_activation_inactive_user_sends_email(
    db, user_factory, client, email_sender_mock
):
    user = await user_factory.create(db, is_active=False)
    await db.commit()

    response = await client.post(
        resend_activation_url,
        json={"email": user.email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == message

    sent_emails = email_sender_mock.get_sent_emails(user.email)
    assert len(sent_emails) == 1
    assert sent_emails[0]["type"] == "activation"
    assert "token" in sent_emails[0]


async def test_resend_activation_nonexistent_email_noop(
    client, faker, email_sender_mock
):
    email = faker.unique.email()

    response = await client.post(
        resend_activation_url,
        json={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == message

    sent_emails = email_sender_mock.get_sent_emails(email)
    assert len(sent_emails) == 0


async def test_resend_activation_active_user_noop(
    db, user_factory, client, email_sender_mock
):
    user = await user_factory.create(db, is_active=True)
    await db.commit()

    response = await client.post(
        resend_activation_url,
        json={"email": user.email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == message

    sent_emails = email_sender_mock.get_sent_emails(user.email)
    assert len(sent_emails) == 0
