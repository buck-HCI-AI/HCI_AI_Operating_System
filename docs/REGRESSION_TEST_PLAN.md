# HCI AI — Regression Test Plan
**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_QA_Testing_and_No_Go_Live_Master_Directive_v1.0

---

## When to Run Regression Tests

| Trigger | Regression Level Required |
|---------|--------------------------|
| Any change to `03_Source_Code/api/` | Smoke test (Level 1) |
| Any change to `03_Source_Code/workflows/` | Smoke test + affected workflow (Level 1-2) |
| Any change to `03_Source_Code/services/` | Smoke test + affected service (Level 1-2) |
| Any schema migration (init.sql change) | Full regression (Level 3) |
| New workflow added | Gate 3 test for new workflow + smoke test |
| Docker compose changes | Full infrastructure regression (Level 3) |
| Before any code merge to main branch | Smoke test minimum |

---

## Level 1 — Smoke Test (2 minutes, run on every code change)

```bash
#!/bin/bash
set -a; source /Users/buckadams/HCI_AI_Operating_System/.env; set +a
API="http://localhost:8000"
KEY="hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c"

echo "=== HCI AI Smoke Test ==="

# 1. Health
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $API/health)
echo "Health: $STATUS (expect 200)"

# 2. Auth — must 401 without key
NO_AUTH=$(curl -s -o /dev/null -w "%{http_code}" $API/api/v1/projects)
echo "No-auth: $NO_AUTH (expect 401)"

# 3. Auth — must 200 with key
WITH_AUTH=$(curl -s -o /dev/null -w "%{http_code}" -H "X-API-Key: $KEY" $API/api/v1/projects)
echo "With-auth: $WITH_AUTH (expect 200)"

# 4. DB check
PG_COUNT=$(psql $DATABASE_URL -t -c "SELECT count(*) FROM projects;" 2>/dev/null | tr -d ' ')
echo "Projects in DB: $PG_COUNT (expect 4)"

# 5. WF-SUPER smoke
WF_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $API/api/v1/workflows/wf-super/daily-log \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"project_number":"TEST-001","work_performed":"[SMOKE TEST]","manpower":0}')
echo "WF-SUPER trigger: $WF_STATUS (expect 200)"

echo "=== Done ==="
```

Save as `Desktop/HCI_Smoke_Test.command` for one-click execution.

**Pass criteria:** All 5 checks match expected values. Any deviation is a regression.

---

## Level 2 — Workflow Regression (10 minutes, run when workflow files change)

Run the specific workflow's test case from `docs/WORKFLOW_TEST_MATRIX.md`.

For example, if `wf_superintendent.py` changed:

```bash
KEY="hci-01253a2b0f87dbd03346bba60f0c31d7350e5c75b17c866c"

# Full WF-SUPER test
curl -s -X POST http://localhost:8000/api/v1/workflows/wf-super/daily-log \
  -H "X-API-Key: $KEY" -H "Content-Type: application/json" \
  -d '{
    "project_number": "TEST-001",
    "work_performed": "[REGRESSION] WF-SUPER test after code change",
    "manpower": 2,
    "weather": "Clear",
    "safety_notes": "None",
    "field_risks": "None"
  }'

# Verify DB write
psql $DATABASE_URL -c "SELECT id, project_number, work_performed FROM daily_logs ORDER BY id DESC LIMIT 1;"

# Verify Qdrant write
curl -s http://localhost:6333/collections/project_memory | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print('Vectors:', d['result']['vectors_count'])"
```

---

## Level 3 — Full Regression (30 minutes, run on schema changes or major refactors)

Run Gate 1 and Gate 2 test suites in full. Document results in `docs/TEST_RESULTS.md` as a new regression section with date.

**Level 3 required before:** any production deployment, any Docker compose change, any schema migration.

---

## Regression History

| Date | Trigger | Level | Result | Issues Found |
|------|---------|-------|--------|-------------|
| 2026-06-25 | Initial build / Phase 12 | Level 1 (informal) | ✅ | Multiple (all fixed - see KNOWN_ISSUES) |

---

## Regression Smoke Test .command File

Create this file so Buck or Claude Code can run it with a double-click:

```bash
# Save to: ~/Desktop/HCI_Smoke_Test.command
# Make executable: chmod +x ~/Desktop/HCI_Smoke_Test.command
```

The smoke test .command file should be created at Gate 1 execution time.
