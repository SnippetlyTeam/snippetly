from abc import ABC, abstractmethod
from typing import Union


class StorageInterface(ABC):
    @abstractmethod
    def upload_file(self, file_name: str, file_data: Union[bytes, bytearray]) -> None:
        """
        Uploads a file to the storage.

        :param file_name: The name of the file to be stored.
        :type: str
        :param file_data: The file data in bytes.
        :type: bytes
        :return: URL of the uploaded file.
        """
        pass

    @abstractmethod
    def get_file_url(self, file_name: str) -> str:
        """
        Generate a public URL for a file.

        :param file_name: The name of the file stored in the bucket.
        :return: The full URL to access the file.
        """
        pass
