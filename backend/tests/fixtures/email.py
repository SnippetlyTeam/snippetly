import pytest_asyncio

from src.core.email import EmailSenderManager
from src.core.email.stub import MockEmailService


@pytest_asyncio.fixture
async def email_sender_stub():
    return EmailSenderManager(
        email_host="smtp.example.com",
        email_port=587,
        email_host_user="noreply@example.com",
        from_email="noreply@example.com",
        use_tls=True,
        app_url="https://myapp.com",
    )


@pytest_asyncio.fixture
async def email_sender_mock(settings, redis_client):
    sender = MockEmailService()
    yield sender
    sender.clear()
