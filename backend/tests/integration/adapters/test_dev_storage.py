from pathlib import Path

import pytest

from src.adapters.storage import DevStorage

TEST_BASE_URL = "http://test-server.com/static/"
TEST_FILE_CONTENT = b"This is test file content."


@pytest.fixture
def dev_storage_instance(tmp_path: Path):
    return DevStorage(base_path=tmp_path, base_url=TEST_BASE_URL)


def test_upload_file_and_get_url_success(
    dev_storage_instance: DevStorage, tmp_path: Path
):
    test_file_name = "test_upload.txt"

    file_url = dev_storage_instance.upload_file(
        test_file_name, TEST_FILE_CONTENT
    )

    expected_path = tmp_path / "static" / "avatars" / test_file_name

    expected_url = TEST_BASE_URL + "avatars/" + test_file_name

    assert file_url == expected_url
    assert expected_path.exists()

    with open(expected_path, "rb") as f:
        content = f.read()
    assert content == TEST_FILE_CONTENT


def test_file_exists_and_delete_file_success(
    dev_storage_instance: DevStorage, tmp_path: Path
):
    test_file_name = "test_delete.bin"

    file_url = dev_storage_instance.upload_file(
        test_file_name, TEST_FILE_CONTENT
    )
    expected_path = tmp_path / "static" / "avatars" / test_file_name

    assert expected_path.exists()
    assert dev_storage_instance.file_exists(file_url) is True

    dev_storage_instance.delete_file(file_url)

    assert not expected_path.exists()
    assert dev_storage_instance.file_exists(file_url) is False


def test_file_exists_for_non_existent_file(dev_storage_instance: DevStorage):
    non_existent_url = TEST_BASE_URL + "avatars/not_here.jpg"
    assert dev_storage_instance.file_exists(non_existent_url) is False


def test_delete_non_existent_file_no_error(dev_storage_instance: DevStorage):
    non_existent_url = TEST_BASE_URL + "avatars/non_exist.png"

    try:
        dev_storage_instance.delete_file(non_existent_url)
    except Exception as e:
        pytest.fail(f"delete_file raised an unexpected exception: {e}")


def test_get_file_url(dev_storage_instance: DevStorage):
    test_file_name = "image_001.jpg"
    expected_url = TEST_BASE_URL + "avatars/" + test_file_name

    url = dev_storage_instance.get_file_url(test_file_name)
    assert url == expected_url
