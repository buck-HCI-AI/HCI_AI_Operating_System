#!/bin/bash
# Called by launchd when HCI_AI_DEV drive mounts.
# Starts Docker services using external drive storage.

LOG="/tmp/hci_docker_drive.log"
INFRA="/Users/buckadams/HCI_AI_Operating_System/infrastructure"

echo "[$(date)] HCI_AI_DEV mounted — starting Docker services..." >> "$LOG"

# Wait for the drive to be fully mounted and writable
sleep 5

# Verify required folders exist on drive
DRIVE="/Volumes/HCI_AI_DEV"
for folder in "03_MinIO_Data" "05_Docker_Volumes/postgres" "05_Docker_Volumes/redis" "05_Docker_Volumes/qdrant"; do
    if [ ! -d "$DRIVE/$folder" ]; then
        echo "[$(date)] ERROR: $DRIVE/$folder missing — aborting" >> "$LOG"
        exit 1
    fi
done

cd "$INFRA" || exit 1

# Start with external storage override
/usr/local/bin/docker compose \
    -f docker-compose.yml \
    -f docker-compose.storage.yml \
    up -d >> "$LOG" 2>&1

echo "[$(date)] Docker services started with external storage" >> "$LOG"
