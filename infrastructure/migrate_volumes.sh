#!/bin/bash
# HCI AI — Migrate Named Docker Volumes → External Drive Bind Mounts
# Run this ONCE when switching from named volumes to HCI_AI_DEV drive.
# Copies data out of Docker-managed volumes into the bind-mount directories.
#
# Usage:
#   HCI_STORAGE_ROOT=/Volumes/HCI_AI_DEV bash infrastructure/migrate_volumes.sh

set -e

STORAGE_ROOT="${HCI_STORAGE_ROOT:-${1:-}}"

if [ -z "$STORAGE_ROOT" ]; then
    echo "ERROR: HCI_STORAGE_ROOT not set."
    echo "Usage: HCI_STORAGE_ROOT=/Volumes/HCI_AI_DEV bash migrate_volumes.sh"
    exit 1
fi

if [ ! -d "$STORAGE_ROOT" ]; then
    echo "ERROR: $STORAGE_ROOT not found. Run setup_storage_drive.sh first."
    exit 1
fi

echo "Migrating Docker volumes to $STORAGE_ROOT ..."
echo "WARNING: Services must be stopped first. Stopping now..."

cd "$(dirname "$0")"
docker compose down

echo ""
echo "Copying Postgres data..."
docker run --rm \
    -v hci_postgres_data:/source:ro \
    -v "$STORAGE_ROOT/05_Docker_Volumes/postgres":/dest \
    alpine sh -c "cp -a /source/. /dest/"

echo "Copying Redis data..."
docker run --rm \
    -v hci_redis_data:/source:ro \
    -v "$STORAGE_ROOT/05_Docker_Volumes/redis":/dest \
    alpine sh -c "cp -a /source/. /dest/"

echo "Copying Qdrant data..."
docker run --rm \
    -v hci_qdrant_data:/source:ro \
    -v "$STORAGE_ROOT/05_Docker_Volumes/qdrant":/dest \
    alpine sh -c "cp -a /source/. /dest/"

echo "Copying MinIO data..."
docker run --rm \
    -v hci_minio_data:/source:ro \
    -v "$STORAGE_ROOT/03_MinIO_Data":/dest \
    alpine sh -c "cp -a /source/. /dest/"

echo ""
echo "Migration complete. Verify data then start with external storage:"
echo "  docker compose -f docker-compose.yml -f docker-compose.storage.yml up -d"
