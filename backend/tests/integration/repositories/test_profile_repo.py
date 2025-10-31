from datetime import date

import pytest

import src.core.exceptions as exc
from src.adapters.postgres.models import GenderEnum

profile_data = {
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "https://example.com/avatar.jpg",
    "gender": GenderEnum.MALE,
    "date_of_birth": date(1990, 1, 1),
    "info": "Some info",
}


async def test_create_profile_empty(db, profile_repo, active_user):
    profile = await profile_repo.create(active_user.id)
    await db.flush()

    assert profile is not None
    assert profile.user_id == active_user.id
    assert profile.first_name == ""
    assert profile.last_name == ""
    assert profile.avatar_url == ""
    assert profile.info == ""
    assert profile.gender is None
    assert profile.date_of_birth is None


async def test_create_profile(db, profile_repo, active_user):
    profile = await profile_repo.create(active_user.id, **profile_data)
    await db.flush()

    assert profile is not None
    assert profile.user_id == active_user.id
    assert profile.first_name == profile_data["first_name"]
    assert profile.last_name == profile_data["last_name"]
    assert profile.avatar_url == profile_data["avatar_url"]
    assert profile.gender == profile_data["gender"]
    assert profile.date_of_birth == profile_data["date_of_birth"]
    assert profile.info == profile_data["info"]


async def test_get_by_user_id_success(db, profile_repo, user_factory):
    user, profile = await user_factory.create_with_profile(db, profile_repo)

    profile_record = await profile_repo.get_by_user_id(user.id)
    assert profile_record is not None


async def test_get_by_user_id_not_found(db, profile_repo, active_user):
    with pytest.raises(exc.ProfileNotFoundError) as e:
        await profile_repo.get_by_user_id(active_user.id)

    assert str(e.value) == "Profile with this user ID was not found"


async def test_get_by_username_success(db, profile_repo, user_factory):
    user, profile = await user_factory.create_with_profile(db, profile_repo)

    profile_record = await profile_repo.get_by_username(user.username)
    assert profile_record is not None


async def test_get_by_username_not_found(db, profile_repo, active_user):
    with pytest.raises(exc.ProfileNotFoundError) as e:
        await profile_repo.get_by_username(active_user.username)

    assert str(e.value) == "Profile with this username was not found"


async def test_update_profile(db, profile_repo, user_factory):
    user, profile = await user_factory.create_with_profile(db, profile_repo)

    await profile_repo.update(user.id, **profile_data)
    await db.flush()
    await db.refresh(profile)

    assert profile.first_name == profile_data["first_name"]
    assert profile.last_name == profile_data["last_name"]
    assert profile.avatar_url == profile_data["avatar_url"]
    assert profile.gender == profile_data["gender"]
    assert profile.date_of_birth == profile_data["date_of_birth"]
    assert profile.info == profile_data["info"]


async def test_update_avatar_url(db, profile_repo, user_factory):
    user, profile = await user_factory.create_with_profile(db, profile_repo)

    await profile_repo.update_avatar_url(user.id, profile_data["avatar_url"])
    await db.flush()
    await db.refresh(profile)

    assert profile.avatar_url == profile_data["avatar_url"]


async def test_delete_avatar_url(db, profile_repo, user_factory):
    user, profile = await user_factory.create_with_profile(db, profile_repo)

    assert profile.avatar_url is not None

    await profile_repo.delete_avatar_url(user.id)
    await db.flush()
    await db.refresh(profile)

    assert profile.avatar_url is None
