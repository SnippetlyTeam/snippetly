from .routes import activate_url


async def test_activate_account_success(db, user_factory, client):
    user, token = await user_factory.create_with_activation_token(db, "token1234")
    await db.commit()

    response = await client.post(
        activate_url,
        json={"activation_token": token}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Account has been activated successfully"

    await db.refresh(user)
    assert user.is_active is True


async def test_activate_account_invalid_token(client):
    response = await client.post(
        activate_url,
        json={"activation_token": "invalid_token_12345"}
    )

    assert response.status_code == 404


async def test_activate_account_expired_token(db, user_factory, activation_token_repo, client):
    user = await user_factory.create(db)
    token = await activation_token_repo.create(user.id, "token1234", -1)
    await db.commit()

    response = await client.post(
        activate_url,
        json={"activation_token": token.token}
    )

    assert response.status_code == 400
