from typing import Union
from urllib.parse import urljoin

import oci

from src.core.config import ProductionSettings
from .interface import StorageInterface


class ProdStorage(StorageInterface):
    def __init__(self, settings: ProductionSettings):
        self._settings = settings

        self.config = {
            "user": settings.ORACLE_USER_OCID,
            "key_file": settings.ORACLE_KEY_FILE_PATH,
            "fingerprint": settings.ORACLE_FINGERPRINT,
            "tenancy": settings.ORACLE_TENANCY_OCID,
            "region": settings.ORACLE_REGION,
        }
        self.client = oci.object_storage.ObjectStorageClient(self.config)

    def upload_file(
        self, file_name: str, file_data: Union[bytes, bytearray]
    ) -> str:
        self.client.put_object(
            self._settings.ORACLE_NAMESPACE,
            self._settings.ORACLE_BUCKET_NAME,
            file_name,
            file_data,
        )
        return self.get_file_url(file_name)

    def get_file_url(self, file_name: str) -> str:
        return urljoin(
            self._settings.ORACLE_BASE_URL,
            f"n/{self._settings.ORACLE_NAMESPACE}"
            f"/b/{self._settings.ORACLE_BUCKET_NAME}/o/{file_name}",
        )

    def delete_file(self, file_url: str) -> None:
        file_name = file_url.split("/o/")[-1]
        self.client.delete_object(
            self._settings.ORACLE_NAMESPACE,
            self._settings.ORACLE_BUCKET_NAME,
            file_name,
        )

    def file_exists(self, file_url: str) -> bool:
        file_name = file_url.split("/o/")[-1]
        try:
            self.client.head_object(
                self._settings.ORACLE_NAMESPACE,
                self._settings.ORACLE_BUCKET_NAME,
                file_name,
            )
            return True
        except oci.exceptions.ServiceError as e:
            if e.status == 404:
                return False
            raise
