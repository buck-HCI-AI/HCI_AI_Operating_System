# BOOK_00 § 14 — Deployment, Backup, and Operations

**Status:** ✅ Production-hardened. Auth live. Backup automated. Monitoring active. Mac mini awaiting hardware.

---

## Current Environment: MacBook Air (Dev/Prod)

| Component | State |
|-----------|-------|
| OS | macOS Sequoia (Darwin 25.5) |
| Python | 3.13 (`/usr/local/bin/python3`) |
| Docker | Running — 4 services (Postgres, Redis, MinIO, Qdrant) |
| FastAPI | launchd-managed, port 8000 |
| Drive | WD My Passport SSD (HCI_AI_DEV, 1 TB) |
| API Auth | Live — `X-API-Key` enforced on `/api/v1/*` |
| Backup | Automated — daily 02:00 AM via launchd |
| Monitoring | Active — 5-min health check via launchd |

---

## API Key Authentication

**Key:** `hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6`  
**Header:** `X-API-Key: <key>`  
**Enforced on:** All `/api/v1/*` routes  
**Open paths:** `/health`, `/docs`, `/redoc`, `/openapi.json`, `/api/v1/health`, `/static/*`, `/dashboard`  
**Legacy routes bypass auth:** `/workflows/`, `/projects`, `/vendors`, `/bids`, `/memory`, `/ingest`

To add more keys: add comma-separated values to `HCI_API_KEYS` in `.env` and restart the API.

```bash
# Test auth
curl -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  http://localhost:8000/api/v1/projects
```

---

## Starting the System

**Automatic:** launchd agents start on login.

**Manual:**
```bash
# Start Docker services
cd ~/HCI_AI_Operating_System/infrastructure && docker compose up -d

# Start API (if not running)
launchctl start com.hci.api-server

# Check health
curl http://localhost:8000/health
```

---

## launchd Agents

| Label | Schedule | Function |
|-------|----------|----------|
| `com.hci.api-server` | KeepAlive | FastAPI server on port 8000 |
| `com.hci.morning-brief` | 7 AM daily | Morning brief email |
| `com.hci.drive-watcher` | On drive mount | Docker startup with storage |
| `com.hci.backup` | 2:00 AM daily | Postgres dump + Qdrant snapshots |
| `com.hci.monitor` | Every 5 min | Health check, restart, disk alert |
| `com.ngrok.hci` | KeepAlive | ngrok webhook tunnel |

```bash
# View all HCI agents
launchctl list | grep com.hci

# Check logs
tail -f ~/Library/Logs/hci_monitor.log
tail -f ~/Library/Logs/hci_backup.log

# Manual backup now
bash ~/Desktop/HCI_Backup.command

# Restart API
launchctl kickstart -k gui/$(id -u)/com.hci.api-server
```

---

## Backup System

**Script:** `03_Source_Code/scripts/backup.sh`  
**Schedule:** Daily at 02:00 AM (launchd `com.hci.backup`)  
**Manual trigger:** Double-click `~/Desktop/HCI_Backup.command`

### What's backed up

| Item | Method | Format |
|------|--------|--------|
| Postgres | `pg_dump -Fc` via docker exec | `.dump` (custom binary, 3-10x smaller than SQL) |
| Qdrant | Snapshot API → download | `.snapshot` per collection |
| MinIO | Bucket manifest | `.txt` listing (data is in Docker named volumes) |

### Destinations

| Priority | Path | When Used |
|----------|------|-----------|
| Primary | `/Volumes/HCI_AI_DEV/backups/YYYYMMDD/` | Drive mounted |
| Fallback | `~/HCI_Backups/YYYYMMDD/` | Drive not available |

**Retention:** 7 days rolling (older dirs auto-deleted each run)

### Restore Postgres from dump

```bash
# From latest backup
LATEST=$(ls -d ~/HCI_Backups/20* | sort | tail -1)
DUMP=$(ls "$LATEST"/postgres_*.dump | tail -1)

docker exec -i hci_postgres pg_restore \
  -U hci_user -d hci_db \
  --no-owner --no-privileges \
  --clean --if-exists \
  < "$DUMP"
```

### Restore Qdrant snapshot

```bash
# Upload snapshot and recover
SNAP_FILE="$LATEST/qdrant/project_memory_20250625_020000.snapshot"
COLL="project_memory"
QDRANT="http://localhost:6333"

# Upload
curl -X POST "$QDRANT/collections/$COLL/snapshots/upload" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@$SNAP_FILE"

# Recover (use snapshot name from upload response)
curl -X POST "$QDRANT/collections/$COLL/snapshots/recover" \
  -H "Content-Type: application/json" \
  -d '{"location": "http://localhost:6333/collections/'"$COLL"'/snapshots/SNAP_NAME"}'
```

---

## Monitoring System

**Script:** `03_Source_Code/scripts/monitor.sh`  
**Schedule:** Every 5 minutes (launchd `com.hci.monitor`)  
**Log:** `~/Library/Logs/hci_monitor.log`

### Checks performed

| Check | Action on Failure |
|-------|-------------------|
| `GET /health` HTTP 200 | `launchctl kickstart` API (3 attempts), then email alert |
| Docker containers running | Email alert with restart command |
| Disk usage < 90% | Email alert with disk details |

### Alert email

Sent to `buck@ahmaspen.com` via Microsoft Graph API (same auth as morning brief / inbox review).

---

## Environment Variables

**File:** `.env` (root, gitignored — never commit)

| Variable | Purpose |
|----------|---------|
| `POSTGRES_PASSWORD` | Postgres container auth |
| `ANTHROPIC_API_KEY` | Claude API for all AI calls |
| `HCI_API_KEYS` | Comma-separated valid API keys |
| `BUCK_EMAIL` | Alert + report delivery address |
| `HCI_BACKUP_DIR` | Primary backup path (defaults to /Volumes/HCI_AI_DEV/backups) |
| `REDIS_PASSWORD` | Redis auth |
| `MINIO_ROOT_USER/PASSWORD` | MinIO access |

---

## Phase 11 — Mac mini Migration (M4 Pro)

**Script:** `infrastructure/setup_mac_mini.sh` — full 14-step automated playbook.

```bash
# Full run (steps 1-14)
bash infrastructure/setup_mac_mini.sh

# Resume from specific step
bash infrastructure/setup_mac_mini.sh --step 6
```

### Step summary

| Step | Task | Manual Action Required? |
|------|------|------------------------|
| 1 | Homebrew + git, jq, curl | No |
| 2 | Python 3.12 | No |
| 3 | Docker Desktop | ✅ Yes — download installer |
| 4 | Repo transfer | ✅ Yes — USB/rsync/git |
| 5 | .env configuration | ✅ Yes — fill in secrets |
| 6 | Docker stack up | No |
| 7 | Schema migration | No |
| 8 | Qdrant restore | No (auto-finds latest backup) |
| 9 | Postgres restore | No (auto-finds latest dump) |
| 10 | Python deps | No |
| 11 | API server launchd | No |
| 12 | Backup + monitor agents | No |
| 13 | ngrok tunnel | ✅ Yes — authtoken config |
| 14 | Smoke test | No |

### Pre-migration checklist

- [ ] Run `bash ~/Desktop/HCI_Backup.command` on MacBook Air to get fresh backup
- [ ] Copy backup from `~/HCI_Backups/` to USB drive or set up LAN rsync
- [ ] Copy `~/.env` from MacBook Air (never push to git)
- [ ] Note ngrok authtoken (in `.env`)
- [ ] Transfer `~/Library/LaunchAgents/com.hci.*.plist` files to Mac mini
