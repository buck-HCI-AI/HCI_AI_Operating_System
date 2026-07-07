#!/usr/bin/env bash
# Double-click this to run a full HCI AI OS backup right now.
# Backs up: repo (rsync), Postgres (pg_dump), Qdrant (snapshot API), MinIO (manifest).
# Goes to the external drive (/Volumes/HCI_AI_DEV*) if it's connected, otherwise
# falls back to ~/HCI_Backups on the internal disk.
cd "$(dirname "$0")"
bash /Users/buckadams/HCI_AI_Operating_System/03_Source_Code/scripts/backup.sh
echo
echo "Done. Press any key to close this window."
read -n 1
