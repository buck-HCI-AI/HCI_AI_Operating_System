# 06_NEXT_SESSION.md
**Exact starting point for next Claude Code session**
Last updated: 2026-06-26 (MVP Sprint 1 COMPLETE)

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
     http://localhost:8000/api/v1/mvp/executive-report

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
