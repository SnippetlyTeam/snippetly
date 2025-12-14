import pytest_asyncio

from .routes import profile_url, avatar_url


@pytest_asyncio.fixture
async def another_user_with_profile(db, user_factory, profile_repo):
    user, profile = await user_factory.create_with_profile(db, profile_repo)
    await db.commit()
    return user, profile


async def test_get_profile_success(auth_client):
    client, user = auth_client
    response = await client.get(profile_url)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user.username
    assert data["first_name"] == user.profile.first_name
    assert data["last_name"] == user.profile.last_name
    assert data["info"] == user.profile.info


async def test_get_profile_unauthorized(client):
    response = await client.get(profile_url)
    assert response.status_code == 401


async def test_get_specific_user_profile_success(
    auth_client, another_user_with_profile
):
    client, _ = auth_client
    user, profile = another_user_with_profile
    response = await client.get(f"{profile_url}{user.username}")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user.username
    assert data["first_name"] == profile.first_name
    assert data["last_name"] == profile.last_name
    assert data["info"] == profile.info


async def test_get_specific_user_profile_not_found(auth_client):
    client, _ = auth_client
    response = await client.get(f"{profile_url}non_existent_user")
    assert response.status_code == 404


async def test_get_specific_user_profile_unauthorized(client):
    response = await client.get(f"{profile_url}some_user")
    assert response.status_code == 401


async def test_update_profile_invalid_data(auth_client):
    client, _ = auth_client
    profile_data = {
        "first_name": 123,
        "last_name": "Doe",
        "info": "Test info",
    }
    response = await client.patch(profile_url, json=profile_data)
    assert response.status_code == 422


async def test_update_profile_unauthorized(client):
    profile_data = {
        "first_name": "John",
        "last_name": "Doe",
        "info": "Test info",
    }
    response = await client.patch(profile_url, json=profile_data)
    assert response.status_code == 401


async def test_update_profile_success(auth_client):
    client, user = auth_client
    profile_data = {
        "first_name": "John",
        "last_name": "Doe",
        "info": "Test info",
    }
    response = await client.patch(profile_url, json=profile_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == profile_data["first_name"]
    assert data["last_name"] == profile_data["last_name"]
    assert data["info"] == profile_data["info"]


async def test_delete_profile_avatar_success(auth_client, avatar_file):
    client, _ = auth_client
    await client.post(avatar_url, files={"avatar": avatar_file})
    response = await client.delete(avatar_url)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Profile avatar has been deleted successfully"
    }


async def test_delete_profile_avatar_unauthorized(client):
    response = await client.delete(avatar_url)
    assert response.status_code == 401


async def test_set_profile_avatar_invalid_format(auth_client):
    client, _ = auth_client
    with open("tests/invalid_avatar.txt", "rb") as f:
        response = await client.post(avatar_url, files={"avatar": f})
    assert response.status_code == 422


async def test_set_profile_avatar_unauthorized(client, avatar_file):
    response = await client.post(avatar_url, files={"avatar": avatar_file})
    assert response.status_code == 401


async def test_set_profile_avatar_success(auth_client, avatar_file):
    client, _ = auth_client
    response = await client.post(avatar_url, files={"avatar": avatar_file})
    assert response.status_code == 200
    assert response.json() == {"message": "Profile picture updated"}
