# Chapter 23 — Backup & Recovery
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 23.1 What Gets Backed Up and When

Every night at 2:00 AM, the backup system runs two operations:
1. **rsync** — copies all source code and documents to the external drive
2. **pg_dump** — exports the full PostgreSQL database to a timestamped file

**External drive:** `/Volumes/HCI_AI_DEV ` (note the trailing space — always quote this path)  
**Drive capacity:** 931 GB  
**Backup path:** `/Volumes/HCI_AI_DEV /backups/`

---

## 23.2 Backup Configuration

The backup is managed by a launchd plist (daily 2 AM).

**Setup status:** `SETUP_DAILY_BACKUP.command` on Desktop — Buck must run this once to activate.

**What SETUP_DAILY_BACKUP.command does:**
1. Creates `/usr/local/bin/hci_daily_backup.sh` with the rsync + pg_dump script
2. Installs launchd plist at `~/Library/LaunchAgents/com.hci.daily.backup.plist`
3. Loads the plist so it fires at 2 AM every day
4. Requires Terminal Full Disk Access (System Settings → Privacy & Security → Full Disk Access → add Terminal)

**To activate if not yet done:**
```
Double-click SETUP_DAILY_BACKUP.command on Desktop
→ Grant Full Disk Access to Terminal when prompted
→ Backup will run tonight at 2 AM
```

---

## 23.3 Manual Backup (Any Time)

Run a manual backup immediately:
```bash
"/usr/local/bin/hci_daily_backup.sh"
```

Or manually:
```bash
# rsync backup
rsync -av --progress \
  /Users/buckadams/HCI_AI_Operating_System/ \
  "/Volumes/HCI_AI_DEV /backups/$(date +%Y-%m-%d)/"

# DB backup
docker exec hci_postgres pg_dump -U hci_admin hci_os > \
  "/Volumes/HCI_AI_DEV /backups/db/hci_os_$(date +%Y%m%d_%H%M%S).sql"

echo "Backup complete"
```

---

## 23.4 Verifying Backups

```bash
# List backup directories
ls "/Volumes/HCI_AI_DEV /backups/"

# Check latest DB backup size (should be 10+ MB)
ls -lh "/Volumes/HCI_AI_DEV /backups/db/" | tail -5

# Verify today's backup exists
TODAY=$(date +%Y-%m-%d)
[ -d "/Volumes/HCI_AI_DEV /backups/$TODAY" ] && echo "TODAY'S BACKUP EXISTS" || echo "NO BACKUP TODAY"
```

---

## 23.5 Recovery Procedures

### Scenario 1: Code File Lost or Corrupted
```bash
# Copy specific file from backup
rsync -av "/Volumes/HCI_AI_DEV /backups/2026-06-30/03_Source_Code/api/routers/gbt_gateway.py" \
  /Users/buckadams/HCI_AI_Operating_System/03_Source_Code/api/routers/gbt_gateway.py
```

### Scenario 2: Database Data Loss (Table or Rows)
```bash
# Restore specific table from backup
# 1. Extract the table from the dump
BACKUP="/Volumes/HCI_AI_DEV /backups/db/hci_os_LATEST.sql"
grep -A999999 "COPY public.vendors " $BACKUP | grep -B999999 "^\\\." > /tmp/vendors_restore.sql

# 2. Restore
docker exec hci_postgres psql -U hci_admin -d hci_os < /tmp/vendors_restore.sql
```

### Scenario 3: Full Database Loss
```bash
# Restore full DB from latest dump
LATEST=$(ls -t "/Volumes/HCI_AI_DEV /backups/db/" | head -1)
docker exec hci_postgres psql -U hci_admin -d hci_os < "/Volumes/HCI_AI_DEV /backups/db/$LATEST"
```

### Scenario 4: Mac mini Migration (Expected ~2026-09)
The backup structure is designed for easy migration to the new M4 Pro Mac mini.

1. Connect external drive to new Mac mini
2. Install Docker, Python 3.13, ngrok
3. Run `infrastructure/setup_mac_mini.sh` (playbook at that path)
4. rsync from drive to new machine
5. Restore DB from latest dump
6. Restart all services
7. Update ngrok domain (if different)
8. Verify all 4 projects healthy

---

## 23.6 Backup Schedule Summary

| When | What | Where |
|------|------|-------|
| Daily 2:00 AM | rsync all source code + docs | `/Volumes/HCI_AI_DEV /backups/YYYY-MM-DD/` |
| Daily 2:05 AM | pg_dump full database | `/Volumes/HCI_AI_DEV /backups/db/hci_os_TIMESTAMP.sql` |
| After every major build | Manual rsync | Same path |
| Before migrations | Manual pg_dump | `/Volumes/HCI_AI_DEV /backups/db/pre_migration_TIMESTAMP.sql` |

---

## 23.7 What Is NOT Backed Up (and Where It Lives)

| Data | Where It Lives | Why Not in rsync |
|------|---------------|-----------------|
| .env file | `/Users/buckadams/HCI_AI_Operating_System/.env` | **IS backed up** — rsync includes it. Keep drive physically secure. |
| n8n workflows | n8n UI + exported JSONs in `workflows/n8n/` | JSONs are backed up via rsync |
| Qdrant vectors | docker volume | Qdrant can rebuild from source data — not critical to snapshot |
| Redis cache | In-memory + docker volume | Ephemeral — cache auto-rebuilds |
| GBT conversation history | ChatGPT cloud | Not in our control — document key decisions in handbook |

---

## 23.8 Before Any Destructive Operation

Before any operation that deletes or overwrites data:

```bash
# Quick backup
BACKUP_DIR="/Volumes/HCI_AI_DEV /backups/pre_op_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
docker exec hci_postgres pg_dump -U hci_admin hci_os > "$BACKUP_DIR/db_snapshot.sql"
echo "Backup at: $BACKUP_DIR"
```

**This is required before:** any `DROP TABLE`, `DELETE FROM` without WHERE, `TRUNCATE`, or `UPDATE` affecting more than 100 rows.

No destructive operations without backup + Buck's confirmation. No exceptions.

---

*Cross-reference: Chapter 22 (Database), Chapter 26 (Emergency), Chapter 31 (Change Management)*
