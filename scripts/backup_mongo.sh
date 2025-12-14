#!/usr/bin/env bash
# Simple MongoDB backup script for Snippetly
# - Runs mongodump inside the MongoDB container
# - Copies the archive to the host backups directory
# - Uploads to Azure Blob Storage using backend image + Azure SDK
# Requirements:
# - docker and docker compose installed on the VM
# - backend/.env contains Azure vars: AZURE_STORAGE_* and containers
# Usage: ./scripts/backup_mongo.sh

set -euo pipefail

# Determine project root directory dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUPS_DIR="$ROOT_DIR/backups"
mkdir -p "$BACKUPS_DIR"

TS="$(date -u +%Y%m%d-%H%M%S)"
FNAME="mongo-backup-$TS.archive.gz"

COMPOSE="docker compose -f $ROOT_DIR/docker-compose.yml"

# Check Mongo is responding
$COMPOSE exec -T mongodb sh -lc "mongosh --eval 'db.adminCommand(\"ping\")' --quiet | grep ok"

echo "Creating MongoDB dump inside container..."
$COMPOSE exec -T mongodb sh -lc 'mongodump --archive=/tmp/'"$FNAME"' --gzip --db "$MONGO_DB" --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin'

# Copy dump from mongo container to host

echo "Copying archive to host: $BACKUPS_DIR/$FNAME"
docker compose -f "$ROOT_DIR/docker-compose.yml" cp mongodb:/tmp/$FNAME "$BACKUPS_DIR/$FNAME"

# Verify backup file exists and has reasonable size
echo "Verifying backup integrity..."
if [ ! -f "$BACKUPS_DIR/$FNAME" ]; then
  echo "❌ ERROR: Backup file not found!"
  exit 1
fi

SIZE=$(stat -f%z "$BACKUPS_DIR/$FNAME" 2>/dev/null || stat -c%s "$BACKUPS_DIR/$FNAME")
if [ "$SIZE" -lt 1024 ]; then
  echo "❌ ERROR: Backup file too small ($SIZE bytes), likely incomplete"
  exit 1
fi

# Verify archive is valid gzip
if ! gzip -t "$BACKUPS_DIR/$FNAME" 2>/dev/null; then
  echo "❌ ERROR: Backup archive is corrupted (gzip test failed)"
  exit 1
fi

echo "✅ Backup verification passed (size: $SIZE bytes)"

# Copy file into backend container temp path

echo "Copying archive into backend container..."
docker compose -f "$ROOT_DIR/docker-compose.yml" cp "$BACKUPS_DIR/$FNAME" backend:/tmp/$FNAME

# Upload using backend image (Azure SDK present)
OBJECT_NAME="backups/mongo/$FNAME"

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
