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

ROOT_DIR="/opt/snippetly"
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

# Upload using backend image (Azure SDK present)
OBJECT_NAME="backups/postgres/$FNAME"

echo "Uploading to Azure Blob Storage as $OBJECT_NAME..."
docker compose -f "$ROOT_DIR/docker-compose.yml" exec -T backend \
  python /app/ops/upload_to_azure.py "/tmp/$FNAME" "$OBJECT_NAME"

echo "Done: $FNAME"
