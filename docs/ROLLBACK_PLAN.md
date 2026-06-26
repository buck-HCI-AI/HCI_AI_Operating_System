# HCI AI — Rollback Plan
**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_QA_Testing_and_No_Go_Live_Master_Directive_v1.0

Recovery procedures for every failure scenario. Always verify backup exists before making any rollback decision.

---

## Backup Locations

| Type | Location | Retention |
|------|----------|-----------|
| Postgres pg_dump | `/Volumes/HCI_AI_DEV/backups/` (primary) | 7 days |
| Postgres pg_dump | `~/HCI_Backups/` (fallback) | 7 days |
| Qdrant snapshot | Same directories as above | 7 days |
| MinIO manifest | Same directories as above | 7 days |

**Verify backup before rollback:**
```bash
ls -lth ~/HCI_Backups/ | head -10
# Most recent pg_dump file should be < 24 hours old if backups are running
```

---

## Scenario 1 — API Failure After Code Change

**Symptoms:** API returns 500; curl /health fails; dashboard not loading  
**Time to recover:** < 5 minutes

```bash
# Step 1: Stop API
launchctl stop com.hci.api

# Step 2: Check git log for last change
cd /Users/buckadams/HCI_AI_Operating_System
git log --oneline -5

# Step 3: Revert last commit (if that caused it)
git revert HEAD --no-edit

# Step 4: Restart API
launchctl start com.hci.api

# Step 5: Verify
curl http://localhost:8000/health
```

**Alternative — revert specific file only:**
```bash
git checkout HEAD~1 -- 03_Source_Code/api/main.py
launchctl stop com.hci.api && launchctl start com.hci.api
```

---

## Scenario 2 — Schema Migration Failure

**Symptoms:** Postgres queries fail; API returns 500 on DB-dependent endpoints; `psql` connection fails  
**Time to recover:** 10-30 minutes depending on data volume

```bash
# Step 1: Find most recent backup
ls -lt ~/HCI_Backups/*.dump | head -5
BACKUP_FILE=$(ls -t ~/HCI_Backups/*.dump | head -1)

# Step 2: Drop and recreate database
psql postgresql://hci_admin:${POSTGRES_PASSWORD}@localhost:5432/postgres << 'EOF'
DROP DATABASE IF EXISTS hci_os;
CREATE DATABASE hci_os OWNER hci_admin;
EOF

# Step 3: Restore from backup
pg_restore -U hci_admin -h localhost -d hci_os --no-owner "$BACKUP_FILE"

# Step 4: Verify
psql $DATABASE_URL -c "SELECT count(*) FROM projects;"
# Expected: 4

# Step 5: Restart API
launchctl stop com.hci.api && launchctl start com.hci.api
```

---

## Scenario 3 — Qdrant Data Corruption or Loss

**Symptoms:** Vector search returns 0; collections missing; Qdrant API errors  
**Time to recover:** 5-20 minutes

```bash
# Step 1: Find most recent Qdrant snapshot
ls -lt ~/HCI_Backups/qdrant_snapshot_* | head -5

# Step 2: Restore snapshot via Qdrant API
# (Qdrant snapshot restore requires stopping collections first)
curl -X POST http://localhost:6333/collections/project_memory/snapshots/upload \
  -H "Content-Type: multipart/form-data" \
  -F "snapshot=@~/HCI_Backups/qdrant_snapshot_project_memory_latest.snapshot"

# Step 3: Verify
curl http://localhost:6333/collections/project_memory
# Check vectors_count

# Step 4: If snapshot restore fails, re-run data pipelines:
python3 /Users/buckadams/HCI_AI_Operating_System/03_Source_Code/workflows/mine_hubspot.py
curl -X POST http://localhost:8000/api/v1/workflows/sync/drive \
  -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c"
```

---

## Scenario 4 — Docker Service Failure (Postgres / Redis / Qdrant / MinIO)

**Symptoms:** Container not running; `docker ps` shows exited status  
**Time to recover:** < 5 minutes

```bash
# Check what's down
docker ps -a | grep -E "(postgres|redis|qdrant|minio)"

# Restart all services
cd /Users/buckadams/HCI_AI_Operating_System/infrastructure
docker compose down
docker compose up -d

# Verify all healthy
docker ps
curl http://localhost:6333/healthz   # Qdrant
curl http://localhost:8000/health    # API (after API restart)

# If API didn't auto-restart:
launchctl stop com.hci.api && launchctl start com.hci.api
```

---

## Scenario 5 — Workflow Logic Regression

**Symptoms:** A workflow that previously worked now produces wrong output or fails  
**Time to recover:** < 10 minutes

```bash
# Step 1: Identify which file regressed
git log --oneline 03_Source_Code/workflows/ | head -10

# Step 2: Revert specific workflow file
git checkout HEAD~1 -- 03_Source_Code/workflows/wf_superintendent.py
# (replace with whichever file regressed)

# Step 3: Restart API to reload modules
launchctl stop com.hci.api && launchctl start com.hci.api

# Step 4: Re-test the workflow
curl -X POST http://localhost:8000/api/v1/workflows/wf-super/daily-log \
  -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c" \
  -H "Content-Type: application/json" \
  -d '{"project_number":"TEST-001","work_performed":"[TEST] regression check","manpower":0}'
```

---

## Scenario 6 — ngrok Tunnel Down (External Access Lost)

**Symptoms:** ngrok URL returns connection refused; remote GPT access fails  
**Time to recover:** < 3 minutes

```bash
# Check ngrok status
launchctl list | grep ngrok
cat /tmp/ngrok-hci.log | tail -20

# Restart ngrok agent
launchctl stop com.ngrok.hci
launchctl start com.ngrok.hci

# Verify
curl https://speculate-armband-retinal.ngrok-free.dev/health
```

---

## Scenario 7 — launchd API Agent Not Running

**Symptoms:** API not reachable on port 8000; nothing on curl /health  
**Time to recover:** < 2 minutes

```bash
# Check status
launchctl list | grep hci.api

# Reload agent
launchctl unload ~/Library/LaunchAgents/com.hci.api.plist
launchctl load ~/Library/LaunchAgents/com.hci.api.plist

# If plist is missing or broken
cd /Users/buckadams/HCI_AI_Operating_System
source .env
uvicorn 03_Source_Code.api.main:app --host 0.0.0.0 --port 8000 &
```

---

## Rollback Test (Required for Gate 1)

Before Gate 1 is declared passed, perform one rollback test:

1. Introduce a deliberate syntax error in a workflow file
2. Restart the API — confirm it fails
3. Execute Scenario 5 rollback procedure
4. Confirm API is restored and the workflow succeeds
5. Document result in `docs/TEST_RESULTS.md` EV-10

---

## Escalation

If any rollback scenario takes more than 30 minutes or data appears corrupted:
1. Stop all writes: `launchctl stop com.hci.api`
2. Do not attempt further changes without understanding root cause
3. Check `~/Library/Logs/hci_api.log` and `~/Library/Logs/hci_monitor.log`
4. Contact Claude Code session for diagnosis

---

*Last updated: 2026-06-25*
