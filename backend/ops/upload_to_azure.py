# Upload a local file to Azure Blob Storage using SDK
# Reads Azure credentials from environment variables compatible with
# ProductionSettings
# Usage: python /app/ops/upload_to_azure.py <local_path> <blob_path>

import os
import sys
from azure.storage.blob import BlobServiceClient


def _build_blob_service() -> BlobServiceClient:
    conn = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if conn:
        return BlobServiceClient.from_connection_string(conn)

    account = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
    endpoint = os.environ.get("AZURE_BLOB_ENDPOINT")

    if not account:
        raise SystemExit("ERROR: Missing AZURE_STORAGE_ACCOUNT_NAME")

    if not endpoint:
        endpoint = f"https://{account}.blob.core.windows.net"

    if not key:
        raise SystemExit(
            "ERROR: Missing AZURE_STORAGE_ACCOUNT_KEY or "
            "AZURE_STORAGE_CONNECTION_STRING"
        )

    return BlobServiceClient(account_url=endpoint, credential=key)


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: upload_to_azure.py <local_path> <blob_path>")
        sys.exit(1)

    local_path = sys.argv[1]
    blob_path = sys.argv[2]

    container = (
        os.environ.get("AZURE_BACKUP_CONTAINER")
        or os.environ.get("AZURE_MEDIA_CONTAINER", "media")
    )

    service = _build_blob_service()
    blob_client = service.get_blob_client(container=container, blob=blob_path)

    with open(local_path, "rb") as f:
        blob_client.upload_blob(f, overwrite=True)

    print(f"Uploaded {local_path} to container {container} as {blob_path}")


if __name__ == "__main__":
    main()
