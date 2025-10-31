from typing import Union
from urllib.parse import urljoin
from uuid import uuid4

from .interface import StorageInterface


class StubStorage(StorageInterface):

    def __init__(self, base_url: str = "http://fake-cdn.com/"):
        self._store = {}  # {file_name: file_data}
        self.base_url = base_url.rstrip('/') + '/'

    def _extract_filename(self, file_url: str) -> str:
        return file_url.split('/')[-1]

    def upload_file(
        self, file_name: str, file_data: Union[bytes, bytearray]
    ) -> str:
        unique_file_name = f"{uuid4()}_{file_name}"

        self._store[unique_file_name] = file_data
        return self.get_file_url(unique_file_name)

    def get_file_url(self, file_name: str) -> str:
        return urljoin(self.base_url, file_name)

    def delete_file(self, file_url: str) -> None:
        file_name = self._extract_filename(file_url)
        if file_name in self._store:
            del self._store[file_name]

    def file_exists(self, file_url: str) -> bool:
        file_name = self._extract_filename(file_url)
        return file_name in self._store
