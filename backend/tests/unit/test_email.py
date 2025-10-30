import aiosmtplib
import pytest


async def test_send_activation_email_success(email_sender_stub, mocker):
    mock = mocker.patch("aiosmtplib.send", return_value=None)

    await email_sender_stub.send_activation_email(
        "user@example.com", "token123"
    )

    mock.assert_called_once()
    message = mock.call_args[0][0]
    assert "Activate your account" in message["Subject"]
    assert "token123" in message.get_content()


async def test_send_email_auth_error(email_sender_stub, mocker):
    mock = mocker.patch(
        "aiosmtplib.send",
        side_effect=aiosmtplib.SMTPAuthenticationError(
            535, "Authentication failed"
        ),
    )

    with pytest.raises(aiosmtplib.SMTPAuthenticationError):
        await email_sender_stub.send_activation_email(
            "user@example.com", "token123"
        )

    mock.assert_called_once()


async def test_send_email_recipient_error(email_sender_stub, mocker):
    mock = mocker.patch(
        "aiosmtplib.send",
        side_effect=aiosmtplib.SMTPRecipientsRefused(
            {"user@example.com": (550, "Mailbox not found")}
        ),
    )

    with pytest.raises(aiosmtplib.SMTPRecipientsRefused):
        await email_sender_stub.send_activation_email(
            "user@example.com", "token123"
        )

    mock.assert_called_once()


async def test_send_email_connect_error(email_sender_stub, mocker):
    mock = mocker.patch(
        "aiosmtplib.send",
        side_effect=aiosmtplib.SMTPConnectError("Connection failed"),
    )

    with pytest.raises(aiosmtplib.SMTPConnectError):
        await email_sender_stub.send_activation_email(
            "user@example.com", "token123"
        )

    mock.assert_called_once()
