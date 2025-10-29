from tests.utils.user import create_user_data
from .routes import register_url, activate_url


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
        "/api/v1/auth/login",
        json={"login": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200
