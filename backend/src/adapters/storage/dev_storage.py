import os
from pathlib import Path
from typing import Union
from urllib.parse import urljoin, urlparse

from .interface import StorageInterface


class DevStorage(StorageInterface):
    def __init__(
        self, base_path: Path, base_url: str = "http://localhost:8000/static/"
    ):
        self.base_url = base_url.rstrip("/") + "/"  # гарантируем слэш
        self.storage_dir = base_path / "static" / "avatars"

    @staticmethod
    def _extract_filename(file_url: str) -> str:
        parsed = urlparse(file_url)
        return Path(parsed.path).name

    def upload_file(
        self, file_name: str, file_data: Union[bytes, bytearray]
    ) -> str:
        os.makedirs(self.storage_dir, exist_ok=True)
        file_path = self.storage_dir / file_name

        with open(file_path, "wb") as f:
            f.write(file_data)

        return self.get_file_url(file_name)

    def get_file_url(self, file_name: str) -> str:
        return urljoin(self.base_url + "avatars/", file_name)

    def delete_file(self, file_url: str) -> None:
        file_name = self._extract_filename(file_url)
        file_path = self.storage_dir / file_name

        if os.path.exists(file_path):
            os.remove(file_path)

    def file_exists(self, file_url: str) -> bool:
        file_name = self._extract_filename(file_url)
        return os.path.exists(self.storage_dir / file_name)
