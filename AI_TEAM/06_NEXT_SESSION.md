# 06_NEXT_SESSION.md
**Exact starting point for next Claude Code session**
Last updated: 2026-06-26 (MVP Sprint 1 COMPLETE)

---

## System State at Session End (2026-06-26, post-Audit + MCP)

**MCP Server:** LIVE — 26 tools, port 8080, ngrok `/mcp`  
**AI Team:** GBT + Claude.ai both connected to MCP  
**HubSpot deal IDs:** Linked for all 3 pilot projects  
**Audit:** 6 deliverables in `HCI_AI_Audit_20260626/`  
**MCP tool fixes:** SOP → /api/v1/sop/registry; HistCost → /search  
**4th project:** id=4 is "83 Sagebrusch Ln." — no HubSpot deal found yet  
**ngrok:** https://speculate-armband-retinal.ngrok-free.dev  

### AI Team Connection Quick Reference
```
MCP endpoint: https://speculate-armband-retinal.ngrok-free.dev/mcp
API Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c (header: X-API-Key)
GBT connect file: /Users/buckadams/Desktop/HCI_AI_GBT_Connect.txt
Claude.ai directive: /Users/buckadams/Desktop/HCI_AI_ClaudeAI_Directive.txt
```

### P0 Tasks Remaining (Buck actions required)
1. n8n: Deactivate/delete duplicate "Bid Receipt Processing v5" (keep active one)
2. n8n: Deactivate "TMP-cl-84994d" (unfinished Outlook→HubSpot webhook)
3. n8n: Retire "ChatGPT Chrome Bridge" (old pre-MCP OpenAI webhook — now superseded)
4. n8n: Go to Settings → API → generate API key → add N8N_API_KEY to .env
5. Google Drive: Archive one copy of HCI_Construction_Operating_System_v2 (keep 03 Registries copy)
6. 83 Sagebrusch (project id=4): Confirm project details / HubSpot deal

### Bid Leveling Quick Commands
```bash
# Dry run — all projects
curl -X POST -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c" \
  -H "Content-Type: application/json" -d '{"dry_run": true}' \
  http://localhost:8000/api/v1/services/bid-leveling/run-all

# Live run — 1355 Riverside divisions 15+16 only
curl -X POST -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c" \
  -H "Content-Type: application/json" -d '{"dry_run": false, "divisions": ["15","16"]}' \
  http://localhost:8000/api/v1/services/bid-leveling/projects/3/run

# GBT: read 1355 Riverside bid data
curl -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c" \
  http://localhost:8000/api/v1/services/bid-leveling/projects/3/data
```

---

## System State at Session End

- API: http://localhost:8000 (live, launchd, auth enforced)
- Dashboard: http://localhost:8000/dashboard
- Docker: Postgres (26 tables), Redis, MinIO, Qdrant all running
- All 9 intelligence services + 3 new MVP services ACTIVE
- 27 SOPs + 6 MVP workflows live and tested
- **MVP Sprint 1: 48/48 tests PASS**
- **Gate 5 pilot: active 2026-06-25 → 2026-07-01**
- Auth: X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c

---

## START HERE — Priority 1: Gate 5 Pilot Operations

The system is live. Buck should be using these daily during the pilot period:

```bash
# Morning briefing — all 3 projects
curl -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c" \
     http://localhost:8000/api/v1/mvp/exec-report

# Check approval queue
curl -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c" \
     "http://localhost:8000/api/v1/services/approval-queue/queue?status=pending"

# Sprint dashboard
curl -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c" \
     http://localhost:8000/api/v1/mvp/sprint-status
```

---

## Priority 2: If Buck Approves Go-Live After Pilot

After Buck's explicit authorization (see `docs/PILOT_READINESS_REPORT.md`):

1. Flip connector registry entries from read_only=TRUE to FALSE (one at a time, by source + project)
2. Enable direct HubSpot write-back for approved workflows
3. Enable Google Drive writes to live folders (not test folders)
4. Document authorization evidence in `docs/PILOT_READINESS_REPORT.md`

---

## Priority 3: Background Learning — Advanced Pipeline

If Buck wants to expand background learning:
- Set up automated Outlook discovery (currently manual)
- Add `extract_and_classify()` to run on all `Discovered` items daily
- Wire intelligence candidates to Buck's morning briefing notification

---

## Rerun Tests Anytime

```bash
python3 /Users/buckadams/HCI_AI_Operating_System/03_Source_Code/tests/test_mvp_sprint_1.py
```

Expected: 48/48 PASS

---

## Key Files Reference

| Purpose | File |
|---------|------|
| MVP workflows | `03_Source_Code/api/routers/mvp_ops.py` |
| Background learning | `03_Source_Code/services/background_learning/` |
| Approval queue | `03_Source_Code/services/approval_queue/` |
| Connector registry | `03_Source_Code/services/connector_registry/` |
| DB schema (MVP Sprint 1) | `03_Source_Code/database/mvp_sprint_1_schema.sql` |
| Test suite | `03_Source_Code/tests/test_mvp_sprint_1.py` |
| User-facing doc | `03_Source_Code/BOOK_01/19_DAILY_OPERATIONS_USING_HCI_AI.md` |
