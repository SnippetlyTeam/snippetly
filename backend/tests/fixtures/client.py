import pytest_asyncio
from httpx import AsyncClient

from src.adapters.postgres.models import UserModel


@pytest_asyncio.fixture
async def auth_client(
    client, auth_service, user_with_profile
) -> tuple[AsyncClient, UserModel]:
    user = user_with_profile[0]
    tokens = await auth_service.login_user(user.email, "Test1234!")
    access_token = tokens["access_token"]
    client.headers["Authorization"] = f"Bearer {access_token}"
    return client, user
