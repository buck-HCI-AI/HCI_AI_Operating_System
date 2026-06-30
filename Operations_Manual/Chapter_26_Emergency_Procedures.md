# Chapter 26 — Emergency Procedures
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 26.1 Emergency Classification

| Level | What's Happening | Response Time | Who Handles |
|-------|----------------|--------------|-------------|
| **P0 — Critical** | All 4 live projects lost data, production DB corrupted, security breach | Immediate | Claude Code + Buck |
| **P1 — High** | API completely down > 30 min, n8n all workflows stopped, data sync failure | < 2 hours | Claude Code |
| **P2 — Medium** | Single workflow failing, one integration down, approval queue stuck | < 24 hours | Claude Code |
| **P3 — Low** | Cosmetic error, report formatting, minor data gap | Next session | Claude Code |

---

## 26.2 P0 — Complete System Recovery

If the entire system is down (Mac restart, power failure, etc.):

```bash
# Step 1: Start Docker (all containers)
cd /Users/buckadams/HCI_AI_Operating_System
docker-compose up -d
sleep 15

# Step 2: Verify DB
docker exec hci_postgres psql -U hci_admin -d hci_os -c "SELECT count(*) FROM projects;"

# Step 3: Restart FastAPI
launchctl stop com.hci.api-server
sleep 2
launchctl start com.hci.api-server
sleep 5

# Step 4: Restart ngrok tunnel
ngrok http 8000 --domain=speculate-armband-retinal.ngrok-free.app &
sleep 5

# Step 5: Verify everything
curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/health | python3 -c "import json,sys; d=json.load(sys.stdin); print('SYSTEM STATUS:', d['status'])"

# Step 6: Send ntfy confirmation
curl -X POST "https://ntfy.sh/hci-ai-os-buck" \
  -H "Title: HCI AI OS — System Restored" \
  -H "Priority: high" \
  -H "Tags: white_check_mark" \
  -d "All services back online after restart. Projects: 64EW, 101F, 1355R, 246GW — verify health."
```

---

## 26.3 P0 — Database Recovery

If the database has corrupted or lost data:

```bash
# Step 1: Identify latest clean backup
ls -lt "/Volumes/HCI_AI_DEV /backups/db/" | head -10

# Step 2: Stop the API (prevent further writes to bad data)
launchctl stop com.hci.api-server

# Step 3: Create a snapshot of current (bad) state before overwriting
docker exec hci_postgres pg_dump -U hci_admin hci_os > /tmp/hci_os_pre_restore_$(date +%Y%m%d).sql

# Step 4: Drop and recreate the database
docker exec hci_postgres psql -U hci_admin -d postgres -c "DROP DATABASE IF EXISTS hci_os;"
docker exec hci_postgres psql -U hci_admin -d postgres -c "CREATE DATABASE hci_os OWNER hci_admin;"

# Step 5: Restore from backup
LATEST=$(ls -t "/Volumes/HCI_AI_DEV /backups/db/"*.sql | head -1)
docker exec -i hci_postgres psql -U hci_admin -d hci_os < "$LATEST"
echo "Restored from: $LATEST"

# Step 6: Restart API
launchctl start com.hci.api-server

# Step 7: Verify
curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/executive/report | python3 -c "import json,sys; print('Projects restored:', len(json.load(sys.stdin)['payload'].get('projects',[])))"
```

**Buck approval required before Step 4.** This overwrites the live database. Confirm with Buck first.

---

## 26.4 P0 — Security Breach

If you suspect the API key has been compromised or unauthorized access:

**Immediate actions:**
1. Rotate the API key: change `HCI_API_KEY` in `.env`, restart FastAPI
2. Check `gateway_request_log` for unauthorized requests:
```sql
SELECT request_timestamp, endpoint, source_ip, api_key_used
FROM gateway_request_log
WHERE request_timestamp > NOW() - INTERVAL '24 hours'
ORDER BY request_timestamp DESC
LIMIT 50;
```
3. If HubSpot was accessed: check HubSpot audit log immediately
4. If Drive was accessed: check Google Drive activity log
5. Notify Buck immediately — do not attempt to handle silently

**New API key format:** `hci-{32 random hex chars}`
Generate: `python3 -c "import secrets; print('hci-' + secrets.token_hex(16))"`

---

## 26.5 P1 — API Down (Cannot Restart via launchd)

If launchctl commands aren't working:

```bash
# Kill any existing uvicorn
pkill -f "uvicorn main:app"
sleep 2

# Start manually in background
cd /Users/buckadams/HCI_AI_Operating_System/03_Source_Code
nohup /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
  -m uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  > /tmp/uvicorn.log 2>&1 &

echo "API PID: $!"

# Monitor startup
tail -f /tmp/uvicorn.log
```

---

## 26.6 P1 — n8n All Workflows Stopped

If Buck reports not receiving morning briefs for 2+ days, n8n may be down.

```bash
# Check n8n container
docker ps --filter "name=n8n"

# Restart n8n
docker restart $(docker ps -qf "name=n8n")
sleep 15

# Verify n8n is up
curl -s http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: $(grep N8N_API_KEY /Users/buckadams/HCI_AI_Operating_System/.env | cut -d= -f2)" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(f'{len([w for w in d[\"data\"] if w[\"active\"]])} workflows active')"

# Check if workflows are still set to active
# If they lost active status, re-activate via n8n UI or API
```

---

## 26.7 P1 — External Drive Not Mounting (Backup Failure)

```bash
# Check if drive is connected
ls /Volumes/

# Mount the drive (macOS usually auto-mounts)
diskutil list | grep -i "HCI"
diskutil mount /dev/disk{N}s{M}  # use the correct disk identifier

# Verify path (trailing space is real)
ls "/Volumes/HCI_AI_DEV /"

# Run manual backup after mount
"/usr/local/bin/hci_daily_backup.sh"
```

If the drive can't mount, back up to a local directory:
```bash
mkdir -p /tmp/hci_emergency_backup
rsync -av /Users/buckadams/HCI_AI_Operating_System/ /tmp/hci_emergency_backup/
docker exec hci_postgres pg_dump -U hci_admin hci_os > /tmp/hci_emergency_backup/hci_os_$(date +%Y%m%d).sql
echo "Emergency backup at /tmp/hci_emergency_backup"
```

---

## 26.8 P2 — Integration Failure (Single Connector)

### HubSpot sync stopped
```bash
# Test HubSpot connectivity
curl -s "http://localhost:8000/api/v1/services/hubspot/health" | python3 -c "import json,sys; print(json.load(sys.stdin))"

# Re-trigger sync
curl -X POST "http://localhost:8000/api/v1/services/hubspot/sync" -d '{"entity": "contacts"}'
```

### Drive scan stopped
1. Open n8n UI → Find AUTO-EVENT-DRIVE-SCAN
2. Check execution history for error
3. Most common: Google OAuth token expired → refresh in n8n Settings → Credentials → Google Drive

### Outlook/Graph API stopped
```bash
# Test Graph token
python3 -c "
import sys
sys.path.insert(0, '/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/integrations')
from credentials import get_ms_token
token = get_ms_token()
print('Token OK:', len(token) > 100)
"
```

---

## 26.9 Emergency Contact Protocol

**If Claude Code can fix it → Fix it, notify Buck via ntfy.**  
**If it requires Buck's physical action → Create a `.command` file on Desktop.**  
**If it requires a business decision → Tell Buck in conversation, do not act.**

Emergency ntfy template:
```bash
curl -X POST "https://ntfy.sh/hci-ai-os-buck" \
  -H "Title: ⚠️ HCI AI OS — [ISSUE TITLE]" \
  -H "Priority: urgent" \
  -H "Tags: warning" \
  -d "[1-2 sentence description of issue and immediate status]"
```

---

## 26.10 Post-Incident Protocol

After any P0 or P1 incident:
1. Write an incident summary (what failed, what was done, when restored)
2. Add to `architecture/CHANGELOG.md` with `[INCIDENT]` tag
3. Update this chapter if a new failure mode was discovered
4. Add a lesson to `lessons_learned` table:
```sql
INSERT INTO lessons_learned (project_id, lesson_type, title, description, source_reference)
VALUES (NULL, 'system_ops', 'Incident: [title]', '[what happened and fix]', 'Chapter 26 post-incident');
```

---

*Cross-reference: Chapter 17 (Architecture), Chapter 22 (Database), Chapter 23 (Backup), Chapter 25 (Troubleshooting)*
