# HCI AI — Test Plan
**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_QA_Testing_and_No_Go_Live_Master_Directive_v1.0  
**Status:** Active — Gates 1-3 pending execution

---

## Scope

This test plan covers all 9 intelligence services, 18 active workflows, 3 sync pipelines, all infrastructure components, and 90+ API endpoints in the HCI AI Construction Operating System.

**Out of scope:** Houzz Playwright scraping (blocked by anti-bot; tracked as KI-001 in KNOWN_ISSUES.md).

---

## Test Environment

- **Host:** MacBook Air (current dev/prod machine)
- **API:** `http://localhost:8000` | Auth: `X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6`
- **DB:** PostgreSQL hci_os (22 tables, 4 projects, 392 vendors)
- **Qdrant:** `http://localhost:6333` (13 collections)
- **ngrok:** `https://speculate-armband-retinal.ngrok-free.dev` (external access)

---

## Test Categories (7)

| Cat | Type | Priority | Gate |
|-----|------|----------|------|
| TC-1 | Unit tests (functions, queries, embeds) | High | Gate 1 |
| TC-2 | API endpoint tests (status, schema, auth) | High | Gate 1 |
| TC-3 | Database integration (write → read round-trip) | High | Gate 1-2 |
| TC-4 | Qdrant integration (embed → upsert → search) | High | Gate 1-2 |
| TC-5 | Workflow end-to-end | Critical | Gate 2-3 |
| TC-6 | Intelligence service quality | High | Gate 3-4 |
| TC-7 | Email delivery | High | Gate 2-3 |

---

## Gate 1 — Engineering Validation Test Cases

### TC-2: API Endpoint Tests

**Setup:** API running on localhost:8000

**Test EV-01 — Health endpoints**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"} HTTP 200

curl http://localhost:8000/api/v1/system/health \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"
# Expected: HTTP 200, all components healthy
```

**Test EV-02 — Auth enforcement**
```bash
# Without key — must return 401
curl http://localhost:8000/api/v1/projects
# Expected: HTTP 401

# With key — must return 200
curl -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  http://localhost:8000/api/v1/projects
# Expected: HTTP 200, array of 4 projects
```

**Test EV-03 — Core CRUD endpoints**
```bash
API_KEY="X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"

# Projects
curl -H "$API_KEY" http://localhost:8000/api/v1/projects          # 200, 4 results
curl -H "$API_KEY" http://localhost:8000/api/v1/vendors           # 200, 392 results
curl -H "$API_KEY" http://localhost:8000/api/v1/bids              # 200
curl -H "$API_KEY" http://localhost:8000/api/v1/workflows         # 200, 18 workflows
curl -H "$API_KEY" http://localhost:8000/api/v1/system/status     # 200
```

**Test EV-06 — All 9 intelligence services return 200**
```bash
API_KEY="X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"
BASE="http://localhost:8000/api/v1/services"

curl -H "$API_KEY" "$BASE/project-brain/101-FRANCIS/snapshot"
curl -H "$API_KEY" "$BASE/bid-intelligence/101-FRANCIS/summary"
curl -H "$API_KEY" "$BASE/vendor-intelligence/search?q=concrete"
curl -H "$API_KEY" "$BASE/lessons-learned/search?q=concrete"
curl -H "$API_KEY" "$BASE/procurement/status/101-FRANCIS"
curl -H "$API_KEY" "$BASE/historical-cost/lookup?trade=framing"
curl -H "$API_KEY" "$BASE/schedule-intelligence/variance/101-FRANCIS"
curl -H "$API_KEY" "$BASE/risk-intelligence/flags/101-FRANCIS"
curl -H "$API_KEY" -X POST "$BASE/document-intelligence/upload" \
  -F "file=@/tmp/test.txt" -F "project_number=TEST-001"
```

**Test EV-09 — Workflow trigger (all 18)**
```bash
API_KEY="X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"
for wf in WF-001 WF-002 WF-003 WF-004 WF-005 WF-006 WF-007 WF-SYNC-HS WF-SYNC-DRIVE WF-SYNC-HOUZZ WF-SUPER WF-PM WF-PM-W WF-REPORT-DAILY WF-REPORT-EXEC WF-REPORT-OWNER WF-REPORT-ALERT WF-REPORT-WEEKLY; do
  result=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    "http://localhost:8000/api/v1/workflows/$wf/trigger" \
    -H "$API_KEY" -H "Content-Type: application/json" \
    -d '{"test": true}')
  echo "$wf: $result"
done
```

### TC-3: Database Integration Tests

**Test EV-03db — Write/read round-trip**
```bash
psql $DATABASE_URL << 'EOF'
-- Verify all 22 tables exist
SELECT count(*) as table_count FROM information_schema.tables
  WHERE table_schema = 'public';
-- Expected: 22

-- Verify 4 projects
SELECT count(*) FROM projects;
-- Expected: 4

-- Verify vendors
SELECT count(*) FROM vendors;
-- Expected: 392

-- Verify HubSpot deals
SELECT count(*) FROM hubspot_deals;
-- Expected: ~306
EOF
```

### TC-4: Qdrant Integration Tests

**Test EV-04 — Collection health**
```bash
curl http://localhost:6333/collections
# Expected: 13 collections, all status: green

# Verify counts
for col in project_memory meeting_memory vendor_memory bid_memory drive_memory \
  constitution_memory hci_project_documents hci_sops hci_historical_costs \
  hci_procurement hci_vendor_intelligence hubspot_notes_memory lessons_learned; do
  echo -n "$col: "
  curl -s "http://localhost:6333/collections/$col" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d['result']['vectors_count'])"
done
```

---

## Gate 2 — Integration Testing Test Cases

### TS-01: Daily Field Log — Field to Email

```bash
API_KEY="X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"

# Step 1: Submit daily log
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/workflows/wf-super/daily-log \
  -H "$API_KEY" -H "Content-Type: application/json" \
  -d '{
    "project_number": "TEST-001",
    "work_performed": "[TEST] Poured footing pad E2 — gate integration test",
    "manpower": 4,
    "weather": "Clear",
    "safety_notes": "No incidents",
    "work_performed_detail": "Concrete crew on site. 10 yards poured."
  }')
LOG_ID=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin).get('log_id',''))")
echo "Log ID: $LOG_ID"

# Step 2: Verify DB write
psql $DATABASE_URL -c "SELECT id, project_number, work_performed FROM daily_logs WHERE id=$LOG_ID;"

# Step 3: Verify Qdrant vector
curl -s -X POST http://localhost:6333/collections/project_memory/points/scroll \
  -H "Content-Type: application/json" \
  -d '{"filter":{"must":[{"key":"log_id","match":{"value":'$LOG_ID'}}]},"limit":1}'

# Step 4: Verify report email triggered (check logs)
tail -20 ~/Library/Logs/hci_api.log | grep "field report"
```

**Pass criteria:**
- `log_id` returned in response
- Row exists in `daily_logs`
- Vector exists in `project_memory` with correct payload
- Log shows email sent (or preview output is correct HTML)

### TS-02: Schedule Variance Detection

```bash
# After TS-01, check schedule_variance was created
psql $DATABASE_URL -c \
  "SELECT log_id, variance_days, severity, analysis_summary FROM schedule_variance 
   ORDER BY created_at DESC LIMIT 1;"
```

### TS-03: Morning Brief

```bash
# Trigger morning brief (preview mode — no email send)
curl -s -X POST http://localhost:8000/api/v1/workflows/wf003/morning-brief \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{"preview": true}'
# Expected: JSON with "subject" and "html_body" fields; mentions all 4 projects
```

### TS-04: Project Brain Q&A

```bash
curl -s -X POST http://localhost:8000/api/v1/services/project-brain/101-FRANCIS/query \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the current bid coverage status for 101 Francis?"}'
# Expected: Answer mentioning bid packages, coverage %, or specific trade info
```

### TS-07: Drive Sync

```bash
# Trigger drive sync, count vectors before and after
BEFORE=$(curl -s http://localhost:6333/collections/drive_memory | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['vectors_count'])")

curl -s -X POST http://localhost:8000/api/v1/workflows/sync/drive \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"

AFTER=$(curl -s http://localhost:6333/collections/drive_memory | \
  python3 -c "import sys,json; d=json.load(sys.stdin); print(d['result']['vectors_count'])")
echo "Vectors: $BEFORE → $AFTER"
# Expected: AFTER >= BEFORE (ideally > if drive has content)
```

---

## Gate 3 — Workflow Acceptance Test Cases

See `docs/WORKFLOW_TEST_MATRIX.md` for individual test cases per workflow. Gate 3 passes when all 18 rows have result = PASS or SKIP (with documented reason).

---

## Gate 4 — UAT Test Cases

See `docs/UAT_PLAN.md` for Buck's UAT scenarios and evaluation criteria.

---

## Gate 5 — Pilot

See `docs/PILOT_READINESS_REPORT.md`.

---

## Test Execution Order

1. Confirm infrastructure is running: `docker ps`, `curl /health`
2. Run Gate 1 (EV-01 through EV-12) — document in TEST_RESULTS.md
3. Fix any P0/P1 defects found — re-run affected tests
4. Run Gate 2 (TS-01 through TS-09) — document in TEST_RESULTS.md
5. Run Gate 3 via WORKFLOW_TEST_MATRIX — document per workflow
6. Escalate to Buck for Gate 4 UAT
7. Run pilot; document in PILOT_READINESS_REPORT
8. Await Buck's explicit go-live approval

---

## Known Exclusions

| Component | Reason | Tracked In |
|-----------|--------|-----------|
| WF-SYNC-HOUZZ | Blocked by Houzz anti-bot protection | KI-001 |
| WF-007 (n8n) | Depends on n8n runtime; test separately | KI-002 |
| Email delivery | Preview mode used; real delivery requires live inbox | Verify in UAT |
