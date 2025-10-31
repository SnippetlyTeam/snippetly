from io import BytesIO
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from fastapi import UploadFile

from src.adapters.postgres.repositories import UserProfileRepository
from src.adapters.storage import StubStorage
from src.features.profile import ProfileService


@pytest_asyncio.fixture
async def storage_stub():
    return StubStorage()


@pytest_asyncio.fixture
async def profile_repo(db):
    return UserProfileRepository(db)


@pytest_asyncio.fixture
async def profile_service(db, storage_stub, profile_repo):
    return ProfileService(db, storage_stub, profile_repo)


@pytest.fixture
def mock_upload_file(mocker):
    mock_image_data = b"fake_image_bytes"
    mock_processed_io = BytesIO(mock_image_data)

    mocker.patch(
        "src.features.profile.service.validate_image",
        return_value=mock_processed_io,
    )

    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_avatar.jpg"

    return mock_file
