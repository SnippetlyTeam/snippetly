from typing import Union

from azure.storage.blob import BlobServiceClient

from src.core.config import ProductionSettings
from .interface import StorageInterface


class ProdStorage(StorageInterface):
    def __init__(self, settings: ProductionSettings):
        self._settings = settings

        if settings.AZURE_STORAGE_CONNECTION_STRING:
            self._blob_service = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
        else:
            if not settings.AZURE_BLOB_ENDPOINT:
                endpoint = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            else:
                endpoint = settings.AZURE_BLOB_ENDPOINT
            self._blob_service = BlobServiceClient(
                account_url=endpoint,
                credential=settings.AZURE_STORAGE_ACCOUNT_KEY,
            )

        self._container = settings.AZURE_MEDIA_CONTAINER

    def upload_file(self, file_name: str, file_data: Union[bytes, bytearray]) -> str:
        blob_client = self._blob_service.get_blob_client(
            container=self._container, blob=file_name
        )
        blob_client.upload_blob(file_data, overwrite=True)
        return self.get_file_url(file_name)

    def get_file_url(self, file_name: str) -> str:
        if self._settings.AZURE_BLOB_ENDPOINT:
            base = self._settings.AZURE_BLOB_ENDPOINT.rstrip("/")
        else:
            base = f"https://{self._settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        return f"{base}/{self._container}/{file_name}"

    def delete_file(self, file_url: str) -> None:
        # Expected URL: https://<account>.blob.core.windows.net/<container>/<blob>
        parts = file_url.split("/")
        file_name = parts[-1]
        blob_client = self._blob_service.get_blob_client(
            container=self._container, blob=file_name
        )
        try:
            blob_client.delete_blob()
        except Exception:
            pass

    def file_exists(self, file_url: str) -> bool:
        parts = file_url.split("/")
        file_name = parts[-1]
        blob_client = self._blob_service.get_blob_client(
            container=self._container, blob=file_name
        )
        try:
            blob_client.get_blob_properties()
            return True
        except Exception:
            return False
