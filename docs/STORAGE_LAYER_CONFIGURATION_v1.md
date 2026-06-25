# Storage Layer Configuration v1

## Overview

HCI AI supports two storage modes: **named volumes** (default, laptop mode) and **bind mounts** (external drive mode). The only difference is which compose file is used at startup — no code changes required.

## Drive Requirements

| Use Case | Drive | Format | Name | Size |
|----------|-------|--------|------|------|
| Development | WD My Passport | APFS, GUID | HCI_AI_DEV | 1 TB |
| Production | Mac mini internal or external | APFS, GUID | HCI_AI_PROD | 4 TB+ |

## Folder Structure on HCI_AI_DEV

```
/Volumes/HCI_AI_DEV/
├── 00_Incoming/            — raw files waiting for ingestion
├── 01_Projects/            — per-project working folders
├── 02_Project_Documents/   — organized project document archive
├── 03_MinIO_Data/          — MinIO object storage data root (Docker bind mount)
├── 04_Database_Backups/    — Postgres dumps, export snapshots
├── 05_Docker_Volumes/
│   ├── postgres/           — Postgres 16 data directory (Docker bind mount)
│   ├── redis/              — Redis 7 AOF + RDB files (Docker bind mount)
│   └── qdrant/             — Qdrant vector storage (Docker bind mount)
├── 06_AI_Exports/          — AI summaries, leveling reports, analysis outputs
├── 07_Repository_Backups/  — git bundle backups of the OS repo
├── 08_Archive/             — completed projects, historical docs
└── 09_Temp/                — scratch space, safe to delete
```

## Setup Sequence

### First-time drive setup

```bash
# 1. Format in Disk Utility: APFS, GUID Partition Map, name = HCI_AI_DEV
# 2. Create folder structure:
bash infrastructure/setup_storage_drive.sh
```

### Activate external storage for Docker

```bash
# Add to infrastructure/.env:
HCI_STORAGE_ROOT=/Volumes/HCI_AI_DEV

# Migrate existing named volume data (run once):
bash infrastructure/migrate_volumes.sh

# Start with external storage:
cd infrastructure
docker compose -f docker-compose.yml -f docker-compose.storage.yml up -d
```

### Revert to named volumes (laptop mode, no drive needed)

```bash
cd infrastructure
docker compose up -d   # no -f flag = uses named volumes
```

## Environment Variable

```bash
# infrastructure/.env
HCI_STORAGE_ROOT=/Volumes/HCI_AI_DEV    # dev SSD
# HCI_STORAGE_ROOT=/Volumes/HCI_AI_PROD  # production 4TB (future)
```

## Docker Compose Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Default — named Docker volumes (laptop-safe) |
| `docker-compose.storage.yml` | Override — bind mounts to `${HCI_STORAGE_ROOT}` |

When switching between drives (dev → production), only change `HCI_STORAGE_ROOT` in `.env`. No code or compose file changes needed.

## Data Paths at a Glance

| Service | Named Volume | Bind Mount (HCI_AI_DEV) |
|---------|-------------|--------------------------|
| Postgres | `hci_postgres_data` Docker volume | `05_Docker_Volumes/postgres/` |
| Redis | `hci_redis_data` Docker volume | `05_Docker_Volumes/redis/` |
| MinIO | `hci_minio_data` Docker volume | `03_MinIO_Data/` |
| Qdrant | `hci_qdrant_data` Docker volume | `05_Docker_Volumes/qdrant/` |

## Backup Strategy

```bash
# Postgres dump → HCI_AI_DEV/04_Database_Backups/
pg_dump -h localhost -U hci_admin hci_os > \
  /Volumes/HCI_AI_DEV/04_Database_Backups/hci_os_$(date +%Y%m%d).sql

# Git bundle → HCI_AI_DEV/07_Repository_Backups/
git bundle create /Volumes/HCI_AI_DEV/07_Repository_Backups/hci_os_$(date +%Y%m%d).bundle --all
```
