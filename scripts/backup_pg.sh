#!/usr/bin/env bash
# Simple PostgreSQL backup script for Snippetly
# - Runs pg_dump inside the Postgres container
# - Copies the dump to the host backups directory
# - Uploads to Azure Blob Storage using backend image + Azure SDK
# Requirements:
# - docker and docker compose installed on the VM
# - backend/.env contains Azure vars: AZURE_STORAGE_* and containers
# Usage: ./scripts/backup_pg.sh

set -euo pipefail

# Determine project root directory dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUPS_DIR="$ROOT_DIR/backups"
mkdir -p "$BACKUPS_DIR"

TS="$(date -u +%Y%m%d-%H%M%S)"
FNAME="pg-backup-$TS.dump"

COMPOSE="docker compose -f $ROOT_DIR/docker-compose.yml"

# Create dump inside the Postgres container using its own env vars
# The container env comes from backend/.env via compose env_file

$COMPOSE exec -T db sh -lc 'pg_isready -U "$POSTGRES_USER" -h 127.0.0.1 -p "$POSTGRES_PORT"'

echo "Creating PostgreSQL dump inside container..."
$COMPOSE exec -T db sh -lc 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -F c -f "/tmp/'"$FNAME"'"'

# Copy dump from db container to host

echo "Copying dump to host: $BACKUPS_DIR/$FNAME"
docker compose -f "$ROOT_DIR/docker-compose.yml" cp db:/tmp/$FNAME "$BACKUPS_DIR/$FNAME"

# Copy file into backend container temp path

echo "Copying dump into backend container..."
docker compose -f "$ROOT_DIR/docker-compose.yml" cp "$BACKUPS_DIR/$FNAME" backend:/tmp/$FNAME

# Verify backup integrity
echo "Verifying backup integrity..."
if ! $COMPOSE exec -T db sh -lc 'pg_restore --list /tmp/'"$FNAME"' > /dev/null 2>&1'; then
  echo "❌ ERROR: Backup verification failed! The dump file appears corrupted."
  exit 1
fi

# Check backup file size
SIZE=$(stat -f%z "$BACKUPS_DIR/$FNAME" 2>/dev/null || stat -c%s "$BACKUPS_DIR/$FNAME")
if [ "$SIZE" -lt 1024 ]; then
  echo "❌ ERROR: Backup file too small ($SIZE bytes), likely incomplete"
  exit 1
fi

echo "✅ Backup verification passed (size: $SIZE bytes)"

# Upload using backend image (Azure SDK present)
OBJECT_NAME="backups/postgres/$FNAME"

echo "Uploading to Azure Blob Storage as $OBJECT_NAME..."
docker compose -f "$ROOT_DIR/docker-compose.yml" exec -T backend \
  python /app/ops/upload_to_azure.py "/tmp/$FNAME" "$OBJECT_NAME"

# Verify upload succeeded
if [ $? -eq 0 ]; then
  echo "✅ Upload successful!"
else
  echo "❌ Upload failed!"
  exit 1
fi

echo "✅ Done: $FNAME"
