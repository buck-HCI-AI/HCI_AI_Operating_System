# Background Job Monitoring Register

**MVP Sprint 1 — Job Monitoring**  

---

## Active Background Processes

| Job Name               | Description                                      | Schedule          | Status    |
|------------------------|--------------------------------------------------|-------------------|-----------|
| HCI API Server         | Main FastAPI application (launchd)               | Always-on         | ✅ Active |
| Background Learning    | Read-only discovery from Drive/HubSpot/Houzz     | Manual trigger    | ✅ Ready  |
| Connector Registry     | Tracks source connection status                  | On-demand         | ✅ Ready  |
| Approval Queue         | Holds pending write actions                      | Real-time         | ✅ Active |

---

## API Server (launchd)

**Service label:** `com.hci.api-server`  
**Log files:**
- stdout: `/tmp/hci_api_server.log`
- stderr: `/tmp/hci_api_server_err.log`

**Control commands:**
```bash
launchctl stop com.hci.api-server    # stop
launchctl start com.hci.api-server   # start
launchctl list | grep hci            # check status
```

**Health check:** `GET http://localhost:8000/health`

---

## Background Learning Job

**Trigger:** Manual via API call  
**Endpoint:** `POST /api/v1/services/background-learning/discover/all`

Runs read-only discovery across all 3 source systems. Safe to run at any time — zero writes to source systems.

**Monitor:** `GET /api/v1/services/background-learning/summary`

Returns count by pipeline status. Items at `Human Review Needed` require Buck attention.

---

## Approval Queue Monitor

**Check pending:** `GET /api/v1/services/approval-queue/queue?status=pending`

Items expire after 72 hours by default. Check daily for items needing approval.

**Sprint status (includes all subsystems):** `GET /api/v1/mvp/sprint-status`

---

## Error Log Monitoring

If API startup fails, check:
```bash
tail -50 /tmp/hci_api_server_err.log
```

Common issues:
- `platform` module collision → check `import platform as _stdlib_platform` is first line of main.py
- `no password supplied` → check `.env` file exists and `load_dotenv()` is called in affected module
- `column X does not exist` → check actual table schema in `05_Database/postgres/schema.sql`

---

## Sprint Status Dashboard

`GET /api/v1/mvp/sprint-status` returns a comprehensive system health snapshot:

```json
{
  "sprint": "MVP Sprint 1",
  "mode": "approval_controlled",
  "connector_registry": {"total": 9, "by_source": {...}},
  "background_learning": {"total": 42, "pending_review": 3, "by_status": {...}},
  "approval_queue": {"total": 15, "pending": 2, "by_status": {...}},
  "total_minutes_saved": 487,
  "as_of": "2026-06-26T..."
}
```
