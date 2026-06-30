# Chapter 25 — Troubleshooting Guide
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 25.1 How to Diagnose Quickly

When something isn't working, start here — 3 commands that tell you 90% of what's wrong:

```bash
# 1. Is the gateway alive?
curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/health | python3 -c "import json,sys; d=json.load(sys.stdin); print('API:', d['status'])" 2>/dev/null || echo "GATEWAY DOWN"

# 2. Is the database running?
docker exec hci_postgres psql -U hci_admin -d hci_os -c "SELECT 'DB OK'" 2>/dev/null || echo "DB DOWN"

# 3. Are containers running?
docker-compose ps 2>/dev/null || docker ps --format "{{.Names}}: {{.Status}}"
```

**If everything is green** → the problem is in data or logic, not infrastructure. See Section 25.5.  
**If gateway is down** → see Section 25.2.  
**If DB is down** → see Section 25.3.  
**If containers are down** → see Section 25.4.

---

## 25.2 Gateway / API Issues

### "curl: connection refused" or "ngrok tunnel not found"

**ngrok is down.** The tunnel is what makes the API reachable from GBT and external sources.

```bash
# Check if ngrok is running
pgrep ngrok || echo "ngrok not running"

# Start ngrok (static domain — always use this exact command)
ngrok http 8000 --domain=speculate-armband-retinal.ngrok-free.app &

# Verify after ~5 seconds
curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/health
```

### "Connection refused on localhost:8000"

**FastAPI is down.**

```bash
# Check if uvicorn is running
ps aux | grep uvicorn | grep -v grep

# Restart via launchd
launchctl stop com.hci.api-server
sleep 2
launchctl start com.hci.api-server
sleep 3

# Verify
curl -s http://localhost:8000/api/v1/services/system-auditor/health
```

If launchctl fails: start manually
```bash
cd /Users/buckadams/HCI_AI_Operating_System/03_Source_Code
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 &
```

### "500 Internal Server Error" on a specific endpoint

The API is running but that endpoint has a bug or DB issue.

```bash
# Get the full error
curl -s "https://speculate-armband-retinal.ngrok-free.dev/gateway/{endpoint}" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('errors', 'no errors'), d.get('warnings',''))"

# Check API logs
launchctl log show --predicate 'subsystem == "com.hci.api-server"' --last 5m 2>/dev/null || \
  journalctl -u hci-api --since "5 min ago" 2>/dev/null || \
  echo "Check uvicorn stdout — look in /tmp or nohup.out"
```

### "422 Unprocessable Entity"

Wrong request format. Check that:
- JSON is valid
- Required fields are present
- Field types are correct (integers as integers, not strings)

### "401 Unauthorized"

Missing or wrong API key on a write endpoint. Header must be exactly:
```
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
```

---

## 25.3 Database Issues

### "could not connect to server" / psql connection refused

**PostgreSQL container is down.**

```bash
# Check container status
docker ps --filter "name=hci_postgres" --format "{{.Status}}"

# If not running, start it
docker start hci_postgres

# Wait for postgres to be ready
until docker exec hci_postgres pg_isready -U hci_admin; do sleep 1; done
echo "PostgreSQL ready"

# Verify
docker exec hci_postgres psql -U hci_admin -d hci_os -c "SELECT count(*) FROM projects;"
```

### "column does not exist" errors

Known schema quirks:
- `approval_queue` has NO `amount` column → use `(proposed_payload->>'amount')::numeric`
- `approval_queue` has NO `project_code` column → use `project_id` (integer FK)
- `project_brain_snapshots` has NO `updated_at` → do not include in UPDATE SET
- `rfis` has NO `csi_division` column → removed from all queries
- `project_ai_conversations` column is `queried_at` NOT `created_at`
- `change_orders` table does NOT exist → use `approval_queue WHERE action_type ILIKE '%change_order%'`

### "relation does not exist"

The table doesn't exist. Verify the table name:
```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "\dt" | grep -i "table_name"
```

### Slow queries (API taking > 5 seconds)

Usually a missing index or a full-table scan:
```sql
-- Find slow queries
SELECT query, calls, total_exec_time/calls as avg_ms
FROM pg_stat_statements
ORDER BY avg_ms DESC
LIMIT 10;
```

---

## 25.4 Container Issues

### All containers down (Mac restart or Docker restart)

```bash
cd /Users/buckadams/HCI_AI_Operating_System
docker-compose up -d

# Wait for startup
sleep 10

# Verify
docker-compose ps
```

### n8n not accessible (localhost:5678)

```bash
# Check if running
docker ps --filter "name=n8n"

# Restart n8n container
docker restart $(docker ps -qf "name=n8n")

# Wait
sleep 10

# Verify
curl -s "http://localhost:5678/api/v1/workflows" \
  -H "X-N8N-API-KEY: $(grep N8N_API_KEY /Users/buckadams/HCI_AI_Operating_System/.env | cut -d= -f2)" | \
  python3 -c "import json,sys; print('n8n OK:', len(json.load(sys.stdin)['data']), 'workflows')"
```

### Qdrant not returning results

```bash
# Check Qdrant
curl -s http://localhost:6333/collections | python3 -c "import json,sys; d=json.load(sys.stdin); print('Collections:', len(d['result']['collections']))"

# If down, restart
docker restart $(docker ps -qf "name=qdrant")
```

### Redis not caching

```bash
docker exec $(docker ps -qf "name=redis") redis-cli ping
# If PONG: Redis is running
# If no response: docker restart $(docker ps -qf "name=redis")
```

---

## 25.5 Data / Logic Issues

### Project health not updating

```bash
# Check when last snapshot was taken
docker exec hci_postgres psql -U hci_admin -d hci_os -c "
SELECT p.project_code, MAX(pbs.snapshot_date) as last_snapshot
FROM project_brain_snapshots pbs JOIN projects p ON p.id = pbs.project_id
GROUP BY p.project_code;"

# Force a new snapshot
curl -X POST "http://localhost:8000/api/v1/services/project-brain/{project_id}/refresh"
```

### Mining not running (HubSpot/Drive data stale)

```bash
# Check last mining runs
docker exec hci_postgres psql -U hci_admin -d hci_os -c "
SELECT miner_name, last_run_at, status FROM mining_runs ORDER BY last_run_at DESC LIMIT 10;"

# Trigger manual mining run
curl -X POST "http://localhost:8000/api/v1/services/mining/run-all" \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'
```

### n8n workflow not triggering on schedule

1. Verify workflow is Active (green toggle in n8n UI)
2. Check execution history for errors
3. Verify n8n system clock matches Mac time
4. Check if workflow's Cron expression is correct (n8n uses cron or interval nodes)
5. Try manually triggering: n8n UI → Workflow → Execute Now button

### SSL certificate errors (Python scripts)

macOS Python 3.13 + urllib has SSL issues. Always use `requests` library:
```python
# BAD — causes SSLCertVerificationError
import urllib.request
urllib.request.urlopen(url)

# GOOD — use this instead
import requests
requests.get(url)
requests.post(url, json=data)
```

---

## 25.6 Known Issues (Current)

| Issue | Severity | Status | Workaround |
|-------|---------|--------|-----------|
| AUTO-EOD Gmail OAuth2 | Medium | Active | EOD summary still on ntfy at 19:00 |
| ntfy messages not showing in app | Low | Monitoring | View at ntfy.sh/hci-ai-os-buck in browser |
| BTW-7 Houzz extraction | Medium | Blocked — needs Buck | 15 min extraction per project unlocks field features |
| 246GW no drawings_folder_id | Low | Open | Drive folder needs to be created |
| 1355R no drawings_folder_id | Low | Open | Drawings accessible via shared URL |
| External drive backup not activated | High | Pending | Run SETUP_DAILY_BACKUP.command on Desktop |

---

## 25.7 Getting Help

**If Claude Code can fix it:** Describe the error message and what you were doing. Claude Code will diagnose and fix without being asked step by step.

**If it requires Buck's action:** Claude Code will create a `.command` file on Desktop with the exact commands to run. Never copy/paste from conversation — always use the .command file.

**If it requires GBT:** Claude Code posts a handoff via `/gateway/agent/handoff` and tells Buck.

---

*Cross-reference: Chapter 17 (Architecture), Chapter 18 (Monitoring), Chapter 26 (Emergency)*
