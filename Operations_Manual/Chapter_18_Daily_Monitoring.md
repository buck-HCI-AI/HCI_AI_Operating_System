# Chapter 18 — Daily System Monitoring
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 18.1 What Gets Monitored and When

The system monitors itself. Every morning you wake up to a health report. Every 30 minutes the system checks project health. Every 15 minutes it scans for new documents. You only need to intervene when something crosses a threshold.

**Automated monitoring schedule:**

| Frequency | What Checks | Where Results Go |
|-----------|------------|-----------------|
| Every 15 min | New Drive documents (PDFs) | Learning queue + ntfy if significant |
| Every 30 min | Project health severity crossings | ntfy push if RED/YELLOW change |
| Hourly | HubSpot changes, continuous discovery | Internal log |
| Daily 06:00 | Superintendent morning console | ntfy → Buck's phone |
| Daily 07:00 | Morning brief email | Outlook email to Buck |
| Daily 02:00 | Full system nightly audit | Architecture/audit log |
| Daily 03:00 | Mining engine (HubSpot, Drive, Houzz) | DB + learning queue |
| Nightly | Houzz change detection | DB updates |
| Weekly Fri | Job reports + executive report | Outlook email |
| Monthly 1st | Business review | Outlook email |

---

## 18.2 Morning Health Check (Manual — 60 seconds)

Run this each morning to verify everything is running:

```bash
# Quick system check
curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/health | python3 -c "
import json,sys
d = json.load(sys.stdin)
p = d['payload']
print(f'Status: {p.get(\"status\",\"?\")}')
print(f'API Score: {p.get(\"health_score\",\"?\")} | Services: {p.get(\"service_count\",\"?\")}')
"
```

Expected output:
```
Status: ok
API Score: 96 | Services: 18
```

If the command fails: ngrok is down. See Chapter 26 Emergency Procedures.

---

## 18.3 Project Health Dashboard

Check all 4 projects at once:

```bash
curl -s "https://speculate-armband-retinal.ngrok-free.dev/gateway/executive/report" | python3 -c "
import json,sys
d = json.load(sys.stdin)
projects = d['payload'].get('projects', [])
for p in projects:
    code = p.get('code','?')
    health = p.get('health','?')
    risks = p.get('open_risks',0)
    print(f'{code}: {health} | {risks} risks')
"
```

Expected output (with 4 live projects):
```
64EW: YELLOW | 2 risks
101F: YELLOW | 2 risks  
1355R: GREEN | 0 risks
246GW: GREEN | 0 risks
```

**Health thresholds:**
- 🟢 GREEN: No critical risks, schedule on track, bid packages moving
- 🟡 YELLOW: 1+ high risks OR schedule variance > 3 days OR stalled procurement
- 🔴 RED: Critical path delay OR budget exposure > 10% OR no activity > 5 days

---

## 18.4 Automated Health Alerts

The system sends ntfy push notifications to Buck's phone automatically:

**Triggers for immediate notification:**
- Any project crosses from YELLOW → RED
- New critical risk detected (severity: critical)
- Approval queue item added (requires Buck action)
- Mining engine discovers a significant change (vendor award, new CO, etc.)
- Nightly audit detects a service failure

**ntfy topic:** `hci-ai-os-buck`

You can manually check what was sent:
```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "
SELECT created_at, notification_type, title, project_code
FROM notification_log 
ORDER BY created_at DESC LIMIT 10;"
```

---

## 18.5 Service Health Checks

### PostgreSQL
```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "SELECT count(*) FROM projects;"
```
Expected: Returns a row count. If it errors, the container is down — see Chapter 26.

### n8n Workflows
```bash
curl -s "http://localhost:5678/api/v1/workflows" \
  -H "X-N8N-API-KEY: $(grep N8N_API_KEY /Users/buckadams/HCI_AI_Operating_System/.env | cut -d= -f2)" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); active=[w for w in d['data'] if w['active']]; print(f'Active: {len(active)}')"
```
Expected: `Active: 55`

### Qdrant
```bash
curl -s "http://localhost:6333/collections" | python3 -c "
import json,sys
d=json.load(sys.stdin)
colls = d['result']['collections']
print(f'Collections: {len(colls)}')"
```
Expected: `Collections: 13`

### Redis
```bash
docker exec $(docker ps -qf "name=redis") redis-cli ping
```
Expected: `PONG`

---

## 18.6 Nightly Audit Report

Every night at 02:00 the system auditor runs and logs results to:
- `architecture/audit/` directory
- `gateway_request_log` table
- Constitution compliance checked: `GET /api/v1/services/system-auditor/constitution`

Check the last nightly audit:
```bash
curl -s "https://speculate-armband-retinal.ngrok-free.dev/api/v1/services/system-auditor/latest" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d['payload'], indent=2))" 2>/dev/null || \
  echo "Check architecture/audit/ directory for latest audit file"
```

---

## 18.7 Approval Queue Monitoring

The approval queue is the most important thing to check each morning after health. Items here require Buck's decision.

```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "
SELECT id, action_type, project_id, status, created_at,
       (proposed_payload->>'title') as title
FROM approval_queue 
WHERE status = 'pending_approval'
ORDER BY created_at DESC
LIMIT 20;"
```

Or via gateway:
```bash
curl -s "https://speculate-armband-retinal.ngrok-free.dev/gateway/role/owner" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); q=d['payload'].get('approval_queue',[]); print(f'Pending: {len(q)} items')"
```

**Act on approvals:** 
- POST `/gateway/approvals/{id}/approve` with API key
- POST `/gateway/approvals/{id}/reject` with API key + `{"reason": "..."}`

---

## 18.8 Integration Sync Status

Check when each connector last synced:

```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "
SELECT connector_name, entity_type, last_sync_at, records_synced
FROM connector_sync_state
ORDER BY connector_name, entity_type;"
```

Expected: HubSpot, Google Drive, Outlook all showing syncs within the last 24 hours.

If a connector shows stale sync (> 48 hours): check n8n for failed workflow runs.

---

## 18.9 ROI Tracking

The system tracks time saved for Buck to validate the investment:

```bash
curl -s "https://speculate-armband-retinal.ngrok-free.dev/api/v1/services/executive-reporting/roi-summary" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); p=d['payload']; print(f'Total time saved: {p.get(\"total_minutes_saved\",0)} minutes')"
```

Current baseline (as of Gate 5 GO):
- **1,784 minutes saved (29.7 hours)**
- 62 documents processed
- 31 risks auto-detected

---

## 18.10 What Needs Human Eyes vs. What the System Handles

**System handles automatically:**
- Project health scoring and trending
- Risk detection from data patterns
- Document discovery and queuing for learning
- HubSpot, Drive, Houzz change detection
- Morning briefs and end-of-day summaries
- Nightly backups and audits
- Knowledge graph updates

**Requires Buck's eyes each morning:**
- Approval queue items (contracts, awards, commitments)
- RED health projects (verify the system has it right)
- ntfy alerts from overnight

**Weekly (Friday):**
- Executive report — verify project narratives are accurate
- n8n workflow health — confirm all 55 are still active

---

*Cross-reference: Chapter 17 (Architecture), Chapter 24 (Approval Queue), Chapter 25 (Troubleshooting), Chapter 26 (Emergency)*
