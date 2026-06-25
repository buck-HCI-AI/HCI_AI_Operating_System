#!/bin/bash
# HCI AI — Storage Drive Setup
# Creates the 10-folder structure on the HCI_AI_DEV external drive.
# Run ONCE after formatting the drive as APFS and naming it HCI_AI_DEV.
#
# Usage:
#   bash infrastructure/setup_storage_drive.sh
#   bash infrastructure/setup_storage_drive.sh /Volumes/HCI_AI_DEV  # custom path

set -e

DRIVE="${1:-/Volumes/HCI_AI_DEV}"

if [ ! -d "$DRIVE" ]; then
    echo "ERROR: Drive not found at $DRIVE"
    echo ""
    echo "To format the 1TB WD My Passport as HCI_AI_DEV:"
    echo "  1. Open Disk Utility (Applications → Utilities → Disk Utility)"
    echo "  2. Select 'My Passport' in the sidebar (the physical disk, not partition)"
    echo "  3. Click Erase"
    echo "  4. Name:   HCI_AI_DEV"
    echo "  5. Format: APFS"
    echo "  6. Scheme: GUID Partition Map"
    echo "  7. Click Erase"
    echo "  8. Re-run this script"
    exit 1
fi

echo "Creating HCI AI folder structure on $DRIVE..."

mkdir -p "$DRIVE/00_Incoming"
mkdir -p "$DRIVE/01_Projects"
mkdir -p "$DRIVE/02_Project_Documents"
mkdir -p "$DRIVE/03_MinIO_Data"
mkdir -p "$DRIVE/04_Database_Backups"
mkdir -p "$DRIVE/05_Docker_Volumes/postgres"
mkdir -p "$DRIVE/05_Docker_Volumes/redis"
mkdir -p "$DRIVE/05_Docker_Volumes/qdrant"
mkdir -p "$DRIVE/06_AI_Exports"
mkdir -p "$DRIVE/07_Repository_Backups"
mkdir -p "$DRIVE/08_Archive"
mkdir -p "$DRIVE/09_Temp"

echo ""
echo "Folder structure created:"
ls -la "$DRIVE"
echo ""
echo "Next step — activate external storage in Docker:"
echo "  1. Edit infrastructure/.env: set HCI_STORAGE_ROOT=$DRIVE"
echo "  2. Stop existing services: cd infrastructure && docker compose down"
echo "  3. (Optional) Migrate data: bash infrastructure/migrate_volumes.sh"
echo "  4. Start with external storage:"
echo "     docker compose -f docker-compose.yml -f docker-compose.storage.yml up -d"
echo ""
echo "Done."
