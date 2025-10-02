import os
from pathlib import Path
from typing import Union
from urllib.parse import urljoin

from .interface import StorageInterface


class DevStorage(StorageInterface):
    def __init__(
        self, base_path: Path, base_url: str = "http://localhost:8000/static/"
    ):
        self.base_url = base_url
        self.storage_dir = base_path / "static" / "avatars"

    def upload_file(
        self, file_name: str, file_data: Union[bytes, bytearray]
    ) -> None:
        file_path = os.path.join(self.storage_dir, file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(file_data)

    def get_file_url(self, file_name: str) -> str:
        return urljoin(self.base_url, file_name)

    def delete_file(self, file_name: str) -> None:
        file_path = os.path.join(self.storage_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    def file_exists(self, file_name: str) -> bool:
        return os.path.exists(os.path.join(self.storage_dir, file_name))
