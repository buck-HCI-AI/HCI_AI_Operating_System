# Chapter 19 — API & Gateway Operations
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 19.1 The Two Entry Points

The HCI AI OS has two ways to talk to it:

**1. REST API (localhost:8000)** — Claude Code's interface. Full read/write access to all 427 endpoints. Runs on the local machine only.

**2. GBT Gateway (ngrok URL)** — GBT's interface + Buck's phone. A curated set of read and write endpoints exposed publicly over HTTPS. Authenticated writes, open reads.

---

## 19.2 GBT Gateway — Complete Endpoint Reference

**Base URL:** `https://speculate-armband-retinal.ngrok-free.dev`
**API Key (writes):** `hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6`

### System Endpoints

| Method | Endpoint | Auth | Returns |
|--------|---------|------|---------|
| GET | `/gateway/health` | None | System health score, service count, constitution status |
| GET | `/gateway/services` | None | Full service registry with BTW labels |
| GET | `/gateway/project-state` | None | Full LIVE_PROJECT_STATE.md content |

### Executive & Role Endpoints

| Method | Endpoint | Auth | Returns |
|--------|---------|------|---------|
| GET | `/gateway/executive/report` | None | Morning brief across all projects |
| GET | `/gateway/executive/mission-control` | None | All KPIs, all projects |
| GET | `/gateway/role/owner` | None | Owner command center (all projects, critical risks, approvals, financials) |
| GET | `/gateway/role/office` | None | Admin queue, submittals, overdue RFIs |
| GET | `/gateway/role/accounting` | None | Budget vs committed, bid awards |
| GET | `/gateway/role/client/{code}` | None | Client-facing health, open RFIs, change orders |
| GET | `/gateway/role/trade-partner?vendor=X&code=Y` | None | Vendor's awarded packages and open RFIs |

### Project Endpoints

| Method | Endpoint | Auth | Returns |
|--------|---------|------|---------|
| GET | `/gateway/project/{code}/brain` | None | Full project snapshot (health, risks, budget, schedule) |
| GET | `/gateway/project/{code}/schedule` | None | Schedule status + variance |
| GET | `/gateway/project/{code}/bids` | None | Bid packages and procurement status |
| GET | `/gateway/project/{code}/pm` | None | PM console (health, risks, actions) |
| GET | `/gateway/project/{code}/timeline` | None | Chronological event history (373 events) |
| GET | `/gateway/project/{code}/documents` | None | Documents linked to decisions/risks/COs |
| GET | `/gateway/project/{code}/memory` | None | AI conversation history for project |
| GET | `/gateway/project/{code}/client-comms` | None | Outstanding client communication items |
| GET | `/gateway/project/{code}/action-list` | None | AI-ranked PM action items |

Project codes: `64EW`, `101F`, `1355R`, `246GW`

### Knowledge Graph Endpoints

| Method | Endpoint | Auth | Returns |
|--------|---------|------|---------|
| GET | `/gateway/knowledge/vendor?name=X` | None | Vendor cross-project history and awards |
| GET | `/gateway/knowledge/issues?q=X` | None | Similar issues across all projects (semantic) |
| GET | `/gateway/knowledge/product?name=X` | None | Product usage and vendor matches |
| GET | `/gateway/drive/search?q=X` | None | Google Drive document search |

### Write Endpoints (API Key Required)

| Method | Endpoint | Auth | Action |
|--------|---------|------|--------|
| POST | `/gateway/agent/handoff` | Key | Send task to Claude Code → writes .md to inbox |
| POST | `/gateway/approvals` | Key | Create approval item → ntfy push to Buck |
| POST | `/gateway/drive/write` | Key | Write markdown file directly to Drive |
| POST | `/gateway/batch` | Key | Batch operations (ntfyPush, driveWrite, etc.) |

---

## 19.3 Making API Calls

### From Terminal (curl)
```bash
# Health check
curl -s "https://speculate-armband-retinal.ngrok-free.dev/gateway/health"

# Project brain snapshot
curl -s "https://speculate-armband-retinal.ngrok-free.dev/gateway/project/101F/brain"

# Send handoff to Claude Code
curl -X POST "https://speculate-armband-retinal.ngrok-free.dev/gateway/agent/handoff" \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{"title": "Task title", "body": "Instructions...", "priority": "high", "source": "manual"}'
```

### From Python (integration scripts)
```python
import requests

BASE = "https://speculate-armband-retinal.ngrok-free.dev"
API_KEY = "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"

# Read (no auth)
r = requests.get(f"{BASE}/gateway/project/64EW/brain")
data = r.json()["payload"]

# Write (with auth)
r = requests.post(f"{BASE}/gateway/approvals",
    headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
    json={"action_type": "notify", "title": "...", "body": "..."})
```

---

## 19.4 Response Parsing

Every endpoint returns the same envelope:
```json
{
  "status": "ok",
  "timestamp": "2026-06-30T07:00:00Z",
  "execution_time_ms": 145,
  "source_system": "hci-api",
  "payload": { ...data specific to endpoint... },
  "warnings": ["optional warning messages"],
  "errors": []
}
```

**Always check:** `response["status"] == "ok"` and `len(response["errors"]) == 0`

If `status` is `"error"`: check `errors[]` for the message. Common causes:
- Project code not found → 404 in errors
- DB connection failed → 500 in errors
- Invalid API key → 401 response

---

## 19.5 Uvicorn Process Management

The FastAPI server runs under uvicorn, managed by launchd.

**Check if running:**
```bash
ps aux | grep uvicorn | grep -v grep
```

**Reload after code changes** (uvicorn runs WITHOUT --reload for stability):
```bash
# Get PID
UVICORN_PID=$(pgrep -f "uvicorn main:app")
# Send HUP signal to reload
kill -HUP $UVICORN_PID
# Verify it restarted
sleep 2 && curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/health | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])"
```

**Hard restart:**
```bash
launchctl stop com.hci.api-server
sleep 2
launchctl start com.hci.api-server
```

---

## 19.6 Adding New Endpoints (Claude Code Only)

When adding new gateway endpoints:

1. Add route to `03_Source_Code/api/routers/gbt_gateway.py`
2. Wrap all DB queries in try/except
3. Use `_response(payload)` wrapper — never return raw dict
4. Use `_log(db, endpoint, code, time_ms)` on every request
5. Never expose raw DB passwords, stack traces, or internal IDs
6. Update `SERVICE_REGISTRY` list in gbt_gateway.py with BTW label
7. Test: `curl -s {BASE}/gateway/{new-endpoint}`
8. Update this chapter with the new endpoint

Architecture Freeze v1.0 (2026-06-28): new tables or schema changes require an ACR filed with GBT.

---

## 19.7 API Rate Limiting & Performance

**Current performance targets:**
- Health check: < 100ms
- Project brain snapshot: < 2 seconds
- Executive report: < 3 seconds
- Knowledge graph queries: < 500ms

**Redis caching:** Responses are cached in Redis with TTL. If you're seeing stale data:
```bash
docker exec $(docker ps -qf "name=redis") redis-cli FLUSHALL
```
This clears all cache. Next requests will re-query DB directly.

**n8n API calls:** n8n workflows call the local API at `http://localhost:8000` (not the ngrok URL) for performance. This is correct behavior.

---

## 19.8 Local vs. External API Calls

| Caller | URL to Use | Why |
|--------|-----------|-----|
| n8n workflows | http://localhost:8000 | Fast, no ngrok latency |
| Claude Code scripts | http://localhost:8000 | Direct local access |
| GBT (ChatGPT) | https://speculate-armband-retinal.ngrok-free.dev | Only public access point |
| Buck's curl commands | Either (local preferred) | Local is faster |
| External webhook receivers | https://speculate-armband-retinal.ngrok-free.dev | Required for external callers |

---

*Cross-reference: Chapter 17 (Architecture), Chapter 20 (n8n Workflows), Chapter 25 (Troubleshooting)*
