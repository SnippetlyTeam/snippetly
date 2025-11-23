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

ROOT_DIR="/opt/snippetly"
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

# Copy file into backend container temp path

echo "Copying archive into backend container..."
docker compose -f "$ROOT_DIR/docker-compose.yml" cp "$BACKUPS_DIR/$FNAME" backend:/tmp/$FNAME

# Upload using backend image (Azure SDK present)
OBJECT_NAME="backups/mongo/$FNAME"

echo "Uploading to Azure Blob Storage as $OBJECT_NAME..."
docker compose -f "$ROOT_DIR/docker-compose.yml" exec -T backend \
  python /app/ops/upload_to_azure.py "/tmp/$FNAME" "$OBJECT_NAME"

echo "Done: $FNAME"
