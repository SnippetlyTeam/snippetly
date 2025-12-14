#!/usr/bin/env bash
# Simple Redis backup script for Snippetly
# - Triggers BGSAVE in Redis container
# - Copies the RDB file to the host backups directory
# - Uploads to Azure Blob Storage using backend image + Azure SDK
# Requirements:
# - docker and docker compose installed on the VM
# - backend/.env contains Azure vars: AZURE_STORAGE_* and containers
# Usage: ./scripts/backup_redis.sh

set -euo pipefail

# Determine project root directory dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUPS_DIR="$ROOT_DIR/backups"
mkdir -p "$BACKUPS_DIR"

TS="$(date -u +%Y%m%d-%H%M%S)"
FNAME="redis-backup-$TS.rdb"

COMPOSE="docker compose -f $ROOT_DIR/docker-compose.yml"

# Check Redis is responding
echo "Checking Redis connectivity..."
$COMPOSE exec -T redis redis-cli ping

# Trigger background save
echo "Triggering Redis BGSAVE..."
$COMPOSE exec -T redis redis-cli BGSAVE

# Wait for BGSAVE to complete (check every 2 seconds, max 30 seconds)
echo "Waiting for BGSAVE to complete..."
for i in {1..15}; do
  if $COMPOSE exec -T redis redis-cli LASTSAVE | grep -q '[0-9]'; then
    SAVE_STATUS=$($COMPOSE exec -T redis redis-cli INFO persistence | grep 'rdb_bgsave_in_progress' | cut -d: -f2 | tr -d '\r')
    if [ "$SAVE_STATUS" = "0" ]; then
      echo "✅ BGSAVE completed"
      break
    fi
  fi

  if [ $i -eq 15 ]; then
    echo "❌ ERROR: BGSAVE timed out"
    exit 1
  fi

  sleep 2
done

# Copy RDB file from Redis container to host
echo "Copying RDB file to host: $BACKUPS_DIR/$FNAME"
docker compose -f "$ROOT_DIR/docker-compose.yml" cp redis:/data/dump.rdb "$BACKUPS_DIR/$FNAME"

# Verify backup file exists and has reasonable size
echo "Verifying backup integrity..."
if [ ! -f "$BACKUPS_DIR/$FNAME" ]; then
  echo "❌ ERROR: Backup file not found!"
  exit 1
fi

SIZE=$(stat -f%z "$BACKUPS_DIR/$FNAME" 2>/dev/null || stat -c%s "$BACKUPS_DIR/$FNAME")
if [ "$SIZE" -lt 100 ]; then
  echo "❌ ERROR: Backup file too small ($SIZE bytes), likely incomplete"
  exit 1
fi

# Check RDB file magic number (first 5 bytes should be "REDIS")
if ! head -c 5 "$BACKUPS_DIR/$FNAME" | grep -q "REDIS"; then
  echo "❌ ERROR: Invalid RDB file format"
  exit 1
fi

echo "✅ Backup verification passed (size: $SIZE bytes)"

# Copy file into backend container temp path
echo "Copying backup into backend container..."
docker compose -f "$ROOT_DIR/docker-compose.yml" cp "$BACKUPS_DIR/$FNAME" backend:/tmp/$FNAME

# Upload using backend image (Azure SDK present)
OBJECT_NAME="backups/redis/$FNAME"

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
