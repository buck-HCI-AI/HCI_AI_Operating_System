# 06_NEXT_SESSION.md
**Exact starting point for next Claude Code session**
Last updated: 2026-06-25 (Phase 13 — QA Framework complete)

---

## System State at Session End

- API: http://localhost:8000 (live, launchd, auth enforced)
- Dashboard: http://localhost:8000/dashboard
- Docker: Postgres (22 tables), Redis, MinIO, Qdrant all running
- All 9 intelligence services ACTIVE
- 18 workflows registered and live
- Phases 1-13 complete (Phase 13 = QA Framework installed)
- **MODE: VALIDATION-FIRST — Go-live BLOCKED until 5 gates pass + Buck approves**
- Auth: X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c

---

## START HERE — Priority 1: Gate 1 Engineering Validation

Read: `docs/QA_VALIDATION_STANDARD.md` → `docs/TEST_PLAN.md` §Gate 1 → execute each check → document results in `docs/TEST_RESULTS.md`

**Estimated time:** 45-60 minutes

### Gate 1 Execution Checklist

```bash
set -a; source /Users/buckadams/HCI_AI_Operating_System/.env; set +a
API="http://localhost:8000"
KEY="hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c"
```

- [ ] EV-01: `curl $API/health` → 200
- [ ] EV-02: `curl $API/api/v1/projects` → 401 (no key)
- [ ] EV-02b: `curl -H "X-API-Key: $KEY" $API/api/v1/projects` → 200, 4 projects
- [ ] EV-03: vendors, bids, workflows endpoints all 200
- [ ] EV-04: `curl http://localhost:6333/collections` → 13 collections
- [ ] EV-05: Malformed payload → 422
- [ ] EV-06a-h: All 9 intelligence services → 200 each
- [ ] EV-07: `psql $DATABASE_URL -c "SELECT count(*) FROM projects;"` → 4
- [ ] EV-08: All 18 workflow triggers → 200 (test mode)
- [ ] EV-09: Dashboard loads at /dashboard
- [ ] EV-10: **RUN BACKUP**: `bash 03_Source_Code/scripts/backup.sh` → verify file in ~/HCI_Backups (closes KI-007)
- [ ] EV-11: `bash 03_Source_Code/scripts/monitor.sh` → completes without error
- [ ] EV-12: `curl https://speculate-armband-retinal.ngrok-free.dev/health` → 200

Document each result in `docs/TEST_RESULTS.md` Gate 1 section.

---

## Priority 2 — Gate 2 Integration Testing (after Gate 1 passes)

Run the 9 test scenarios from `docs/TEST_PLAN.md` §Gate 2. Key scenarios:
- TS-01: Full WF-SUPER flow (field log → DB → Qdrant → email)
- TS-03: Morning brief preview
- TS-04: Project Brain Q&A
- TS-07: Drive sync (check KI-010 — drive_memory persistence)

---

## Priority 3 — Gate 3 Workflow Acceptance (after Gate 2 passes)

Work through `docs/WORKFLOW_TEST_MATRIX.md` — run each ⬜ workflow test case and fill in the result column.

---

## Priority 4 — Gate 4 UAT (Buck runs this)

Deliver `docs/UAT_PLAN.md` to Buck and walk him through the 5 Tier 1 scenarios. Results go in `docs/UAT_RESULTS.md`.

---

## Known Issues to Address (in order)

| KI ID | Priority | Action |
|-------|----------|--------|
| KI-007 | High | Run backup.sh and verify output (Gate 1, EV-10) |
| KI-010 | High | Investigate drive_memory persistence after Docker restart |
| KI-003 | Medium | Build vendor embed pipeline (vendors → vendor_memory) |
| KI-001 | Low | Houzz — explore manual export or defer |
| KI-004 | Low | Add workflow_events writes to WF-001, WF-002, WF-005, WF-006 |

---

## Key File Locations

```
QA framework:             BOOK_00/17_QUALITY_ASSURANCE_AND_VALIDATION.md
QA standard (quick ref):  docs/QA_VALIDATION_STANDARD.md
Test plan:                docs/TEST_PLAN.md
Test results (evidence):  docs/TEST_RESULTS.md
Workflow test matrix:     docs/WORKFLOW_TEST_MATRIX.md
Known issues:             docs/KNOWN_ISSUES.md
UAT plan:                 docs/UAT_PLAN.md
Rollback procedures:      docs/ROLLBACK_PLAN.md
System data flow:         docs/SYSTEM_DATA_FLOW.md

FastAPI app:              03_Source_Code/api/main.py
Intelligence services:    03_Source_Code/services/
Workflows:                03_Source_Code/workflows/
DB schema:                infrastructure/postgres/init.sql (authoritative)
API logs:                 ~/Library/Logs/hci_api*.log
Monitor logs:             ~/Library/Logs/hci_monitor.log
```

---

## Rules — Do Not Violate

- Do not write to HubSpot without Buck's explicit approval
- Do not commit .env to git
- Always use env vars for DB credentials (never hardcode passwords)
- Create .command files on Desktop for any shell commands Buck needs to run
- No component advances past "Built - Untested" without documented test evidence
- Production go-live requires Buck's explicit written approval in PILOT_READINESS_REPORT.md
