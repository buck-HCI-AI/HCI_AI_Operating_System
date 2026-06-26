# HCI AI — QA Validation Standard
**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_QA_Testing_and_No_Go_Live_Master_Directive_v1.0  
**Authoritative reference:** `BOOK_00/17_QUALITY_ASSURANCE_AND_VALIDATION.md`

---

## The Rule

**Production go-live is BLOCKED until all 5 validation gates pass and Buck Adams explicitly approves.**

"It worked when I built it" is not test evidence. Every component needs documented output.

---

## 5 Validation Gates (summary)

| Gate | Owner | Evidence Location | Status |
|------|-------|-------------------|--------|
| Gate 1: Engineering Validation | Claude Code | `docs/TEST_RESULTS.md` §Gate1 | ✅ PASSED 2026-06-25 |
| Gate 2: Integration Testing | Claude Code | `docs/TEST_RESULTS.md` §Gate2 | ✅ PASSED 2026-06-25 |
| Gate 3: Workflow Acceptance Testing | Claude Code + Buck | `docs/WORKFLOW_TEST_MATRIX.md` | ✅ PASSED 2026-06-25 |
| Gate 4: User Acceptance Testing | Buck Adams | `docs/UAT_RESULTS.md` | ✅ PASSED 2026-06-25 |
| Gate 5: Pilot Approval + Go-Live Auth | Buck Adams | `docs/PILOT_READINESS_REPORT.md` | ⬜ Ready — 5-day pilot on one project |

---

## 9 Production Status Values

Every workflow, service, and component has exactly one status from this list:

```
1. Not Started          — not built
2. Built - Untested     — code exists; no test evidence
3. Testing              — currently being tested
4. Failed Validation    — test ran; failures found; defect logged
5. Validated in Test    — passed Gate 1/2; evidence documented
6. UAT Ready            — Gates 1-3 passed; ready for Buck
7. UAT Passed           — Buck confirmed output correct and useful
8. Pilot Ready          — cleared for live use on one project
9. Production Ready     — all 5 gates passed; Buck signed off
```

**Rule:** Status advances only when evidence is in `docs/TEST_RESULTS.md` or `docs/UAT_RESULTS.md`.

---

## Defect Severity

| Level | Meaning | Go-Live Impact |
|-------|---------|---------------|
| P0 | Data corruption, security breach, system failure | Hard blocker |
| P1 | Happy-path failure, wrong DB write, email not delivered | Hard blocker |
| P2 | Degrades with workaround | Must fix before UAT |
| P3 | Cosmetic / minor | Backlog only |

All defects → `docs/KNOWN_ISSUES.md` with ID `KI-NNN`.

---

## Test Data Rules

- Test records: `project_number = "TEST-001"` or `"QA-{wf_id}"`
- Notes field: tagged `[TEST]`
- Emails: `--preview` mode or `[TEST]` prefix in subject
- Qdrant vectors: payload `test: true`

---

## Regression Smoke Test (run on every code change)

```bash
# 1. Health
curl http://localhost:8000/health

# 2. Auth
curl -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c" \
  http://localhost:8000/api/v1/projects

# 3. WF-SUPER smoke
curl -X POST http://localhost:8000/api/v1/workflows/wf-super/daily-log \
  -H "X-API-Key: hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c" \
  -H "Content-Type: application/json" \
  -d '{"project_number":"TEST-001","work_performed":"[TEST] regression smoke","manpower":0}'

# 4. DB check
psql $DATABASE_URL -c "SELECT count(*) FROM projects;"
```

---

## Key Documents (full detail)

| Document | Purpose |
|----------|---------|
| `BOOK_00/17_QUALITY_ASSURANCE_AND_VALIDATION.md` | Full QA framework |
| `docs/TEST_PLAN.md` | What to test and how |
| `docs/TEST_RESULTS.md` | Evidence log for Gates 1-3 |
| `docs/WORKFLOW_TEST_MATRIX.md` | All 18 workflows with test cases and results |
| `docs/KNOWN_ISSUES.md` | All open defects |
| `docs/UAT_PLAN.md` | UAT scenarios for Buck |
| `docs/UAT_RESULTS.md` | Buck's UAT evidence |
| `docs/PILOT_READINESS_REPORT.md` | 5-day pilot evidence + go-live approval |
| `docs/ROLLBACK_PLAN.md` | How to recover from failures |
| `docs/REGRESSION_TEST_PLAN.md` | Regression suite |
| `docs/SYSTEM_DATA_FLOW.md` | End-to-end data flow diagram |
