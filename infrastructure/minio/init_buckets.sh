#!/bin/sh
# MinIO bucket initialization — runs via minio-init service in docker-compose
# Called automatically on first startup. Safe to re-run (--ignore-existing).
#
# Bucket strategy per HCI AI Data Architecture v1:
#   hci-raw-documents        — all incoming files, unmodified
#   hci-processed-documents  — extracted text, normalized outputs
#   hci-ai-artifacts         — AI summaries, leveling reports, analysis outputs
#   hci-backups              — Postgres dumps, export snapshots
#   hci-ingestion-quarantine — failed or suspicious ingestion files

set -e

mc alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"

mc mb --ignore-existing local/hci-raw-documents
mc mb --ignore-existing local/hci-processed-documents
mc mb --ignore-existing local/hci-ai-artifacts
mc mb --ignore-existing local/hci-backups
mc mb --ignore-existing local/hci-ingestion-quarantine

echo "Buckets ready:"
mc ls local/
