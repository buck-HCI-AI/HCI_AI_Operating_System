# MVP Sprint 1 — Test Plan

**Test File:** `tests/test_mvp_sprint_1.py`  
**Results File:** `tests/test_results_mvp_sprint_1.json`  
**Coverage:** 48 tests across 12 test groups  

---

## Test Groups

### MS-01: Project Brain Init (4 tests)
- Init returns project baseline for all 3 pilot projects
- MVP overview lists all 6 workflows

### MS-02: Bid Management (4 tests)
- Dry-run returns proposed bid + validation
- Dry-run does NOT write to DB
- Bid import returns ROI metrics
- Bid import with dry_run=False queues for approval (not written directly)

### MS-03: Daily Log + Field Intelligence (5 tests)
- Daily log dry-run returns intelligence analysis
- Delay detected from log notes keyword matching
- Schedule risk detected from delay keywords
- Daily log ROI metrics returned
- Daily log with dry_run=False queues for approval

### MS-04: PM Weekly Review (3 tests — one per pilot project)
- PM weekly review returns health status (green/yellow/red) + metrics for 64EW, 101F, 1355R

### MS-05: Schedule/Status Intelligence (3 tests — one per pilot project)
- Schedule status returns overall_status for 64EW, 101F, 1355R

### MS-06: Executive Reporting (4 tests)
- Exec report returns all 3 pilot projects
- Exec report has summary with risk totals
- Exec report mode is read_only
- Exec report includes ROI

### BL-01: Background Learning (8 tests)
- Service info endpoint
- Discover registers item with status=Discovered
- Project inferred from filename (1355 Riverside)
- Records query returns discovered items
- Classify advances record through pipeline
- HubSpot discovery runs in read_only mode
- Drive discovery runs in read_only mode
- Background learning summary returns totals

### AQ-01: Approval Queue (5 tests)
- Summary returns status breakdown
- Pending queue has items from workflow tests
- Approve action marks item approved
- Reject on already-approved item returns error gracefully
- Approval never auto-executes — requires explicit execute call

### CR-01: Connector Registry (3 tests)
- Init-pilots registers all 9 source connections (3 projects × 3 sources)
- Connectors for 64 Eastwood returns registered sources
- Connector registry summary has totals

### ROI-01: ROI Log (3 tests)
- ROI log populated from workflow tests above
- ROI log shows minutes saved across workflows
- ROI log has individual workflow entries

### SP-01: Sprint Status (3 tests)
- Sprint status endpoint returns all subsystem summaries
- Total minutes saved > 0 after workflow tests
- Sprint mode shows approval_controlled controls active

### SC-01: Safety / Approval Controls (3 tests)
- All write actions are in approval queue (not silently written)
- All pending items have rollback_path specified
- No live DB write occurred without queue entry (by design)

---

## How to Run

```bash
python3 tests/test_mvp_sprint_1.py
```

API must be running on `localhost:8000`. Requires `X-API-Key` header (set in test file).

---

## Pass Criteria

All 48 tests must pass. Any failure blocks Gate 5 go-live authorization.
