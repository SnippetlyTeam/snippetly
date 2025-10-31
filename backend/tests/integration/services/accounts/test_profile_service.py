import pytest
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc
from src.adapters.postgres.models import GenderEnum
from src.api.v1.schemas.accounts import ProfileUpdateRequestSchema

profile_data = ProfileUpdateRequestSchema(
    first_name="John",
    last_name="Doe",
    gender=GenderEnum.MALE,
    info="Some info",
)


async def test_update_profile_success(profile_service, user_with_profile):
    user = user_with_profile[0]

    profile = await profile_service.update_profile(user.id, profile_data)

    assert profile.first_name == profile_data.first_name
    assert profile.last_name == profile_data.last_name
    assert profile.gender == profile_data.gender
    assert profile.info == profile_data.info


async def test_update_profile_not_found(profile_service, active_user):
    with pytest.raises(exc.ProfileNotFoundError):
        await profile_service.update_profile(active_user.id, profile_data)


async def test_update_profile_db_error(
    profile_service, user_with_profile, profile_repo, mocker
):
    mock = mocker.patch(
        "src.features.profile.service.UserProfileRepository.update",
        side_effect=SQLAlchemyError,
    )
    user, profile = user_with_profile[0], user_with_profile[1]

    with pytest.raises(SQLAlchemyError):
        await profile_service.update_profile(user.id, profile_data)

    mock.assert_called_once()
    profile_record = await profile_repo.get_by_user_id(user.id)
    assert profile_record == profile


async def test_set_profile_avatar_success_no_old_avatar(
    profile_service,
    user_with_profile,
    mock_upload_file,
    profile_repo,
    storage_stub,
):
    user, profile = user_with_profile[0], user_with_profile[1]

    assert profile.avatar_url == ""

    await profile_service.set_profile_avatar(user.id, mock_upload_file)

    updated_profile = await profile_repo.get_by_user_id(user.id)
    assert updated_profile.avatar_url != ""
    assert updated_profile.avatar_url.startswith(storage_stub.base_url)

    assert storage_stub.file_exists(updated_profile.avatar_url)


async def test_set_profile_avatar_success_with_old_avatar(
    profile_service,
    user_with_profile,
    mock_upload_file,
    profile_repo,
    storage_stub,
):
    user, profile = user_with_profile[0], user_with_profile[1]

    old_url = storage_stub.upload_file("old_avatar.png", b"old_data")
    await profile_repo.update_avatar_url(user.id, old_url)
    await profile_repo._db.commit()
    await profile_repo._db.refresh(profile)
    assert profile.avatar_url == old_url
    assert storage_stub.file_exists(old_url)

    await profile_service.set_profile_avatar(user.id, mock_upload_file)

    updated_profile = await profile_repo.get_by_user_id(user.id)
    new_url = updated_profile.avatar_url
    assert new_url != ""
    assert new_url != old_url

    assert storage_stub.file_exists(new_url)

    assert not storage_stub.file_exists(old_url)


async def test_set_profile_avatar_db_error_rollback_storage(
    profile_service, user_with_profile, mock_upload_file, mocker, storage_stub
):
    user, profile = user_with_profile[0], user_with_profile[1]

    mock = mocker.patch(
        "src.features.profile.service.UserProfileRepository.update_avatar_url",
        side_effect=SQLAlchemyError,
    )
    assert profile.avatar_url == ""

    with pytest.raises(SQLAlchemyError):
        await profile_service.set_profile_avatar(user.id, mock_upload_file)

    mock.assert_called_once()
    assert profile.avatar_url == ""


async def test_delete_profile_avatar_success(
    profile_service, user_with_profile, profile_repo, storage_stub
):
    user, profile = user_with_profile[0], user_with_profile[1]

    avatar_url = storage_stub.upload_file("test_delete.png", b"file_data")
    await profile_repo.update_avatar_url(user.id, avatar_url)
    await profile_repo._db.commit()
    await profile_repo._db.refresh(profile)
    assert profile.avatar_url == avatar_url
    assert storage_stub.file_exists(avatar_url)

    await profile_service.delete_profile_avatar(user.id)

    updated_profile = await profile_repo.get_by_user_id(user.id)
    assert updated_profile.avatar_url is None

    assert not storage_stub.file_exists(avatar_url)


async def test_delete_profile_avatar_no_avatar(
    profile_service, user_with_profile, storage_stub, mocker
):
    user, profile = user_with_profile[0], user_with_profile[1]
    assert profile.avatar_url == ""

    mock_storage_delete = mocker.spy(storage_stub, "delete_file")

    await profile_service.delete_profile_avatar(user.id)

    mock_storage_delete.assert_not_called()
