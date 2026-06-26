# BOOK_00 §17 — Quality Assurance and Validation
**HCI AI Construction Operating System**  
**Version:** 1.0 | **Adopted:** 2026-06-25 | **Directive:** HCI_AI_QA_Testing_and_No_Go_Live_Master_Directive_v1.0  
**Governance:** Production go-live is BLOCKED until all 5 validation gates pass and Buck Adams explicitly approves.

---

## §17.1 Purpose and Philosophy

The HCI AI Operating System processes real construction data: bid packages, daily field logs, vendor databases, schedule baselines, risk flags, and owner-facing reports. Errors are not cosmetic — a wrong bid amount, a missed risk flag, or a corrupted daily log can have financial and legal consequences on active projects.

This volume establishes the quality assurance framework that governs all code shipped to production. The governing rule is simple:

> **A system component is not production-ready until it has passed all required validation gates, produced documented evidence, and received explicit approval from Buck Adams.**

Testing is not bureaucracy. It is the mechanism by which we know the system does what we say it does.

### Core Principles

1. **Evidence over assertion.** Every gate requires documented output — not "this should work" but "this produced this output on this date."
2. **Honest status.** Every workflow and service carries one of 9 production status values that reflects true test state. No component is "done" just because it was built.
3. **Fail fast.** Defects found in engineering validation are far cheaper than defects found in production. Push issues early.
4. **No data corruption.** Any test that produces corrupted DB records, incorrect Qdrant vectors, or misdirected emails is a P0 defect.
5. **Build for stabilization.** Tests are designed to verify the system holds at scale and over time, not just on initial run.

---

## §17.2 Testing Environments

HCI AI currently operates with a single environment (the Mac Book Air development/production machine). Until the Mac mini M4 Pro arrives (~2026-09-17), testing and production share the same infrastructure.

**Implication:** All tests must use isolated test data that can be identified and cleaned up without touching real project data. Use project_number prefix `TEST-` or `QA-` for all test records.

| Environment | Host | Purpose | Status |
|-------------|------|---------|--------|
| Development / Test | MacBook Air (current) | All active development and QA | Active |
| Production | Mac mini M4 Pro | Future production deployment | Pending hardware |

**Test data isolation rules:**
- All test projects use `project_number = "TEST-001"` or `"QA-{workflow_id}"`
- Test records are tagged in notes fields as `[TEST]`
- Test emails use `--preview` mode where available, or send to `buck@ahmaspen.com` with `[TEST]` subject prefix
- Test Qdrant vectors use payload field `test: true` for identification and cleanup
- Test runs must be logged in `docs/TEST_RESULTS.md`

---

## §17.3 Test Categories (7)

| # | Category | Description | Owner |
|---|----------|-------------|-------|
| TC-1 | Unit Tests | Individual function behavior; DB query correctness; embed text output | Claude Code |
| TC-2 | API Endpoint Tests | HTTP status codes, response schema, auth enforcement, error handling | Claude Code |
| TC-3 | Database Integration Tests | Write → read round-trip; FK constraint validation; schema match | Claude Code |
| TC-4 | Qdrant Integration Tests | Embed → upsert → search round-trip; vector count; similarity match | Claude Code |
| TC-5 | Workflow End-to-End Tests | Trigger → all stages complete → correct DB writes → correct email output | Claude Code + Buck |
| TC-6 | Intelligence Service Tests | Service query → correct data synthesis → useful output for Buck's use cases | Buck |
| TC-7 | Email Delivery Tests | Report generation → graph API send → receipt confirmation at buck@ahmaspen.com | Buck |

---

## §17.4 Test Scenarios (9)

The following 9 scenarios form the backbone of the system's acceptance criteria. Each must be documented in `docs/TEST_RESULTS.md`.

| # | Scenario | Workflows / Services Exercised |
|---|----------|-------------------------------|
| TS-01 | Daily Field Log — Field to Email | WF-SUPER → WF-REPORT-DAILY → email delivered |
| TS-02 | Schedule Variance Detection | WF-SUPER → analyze_log → schedule_variance alert generated |
| TS-03 | Morning Brief Sequence | WF-SYNC-HS → WF-003 → email with all-project status |
| TS-04 | Bid Package Q&A | WF-SYNC-HS → project-brain → bid-intelligence → useful Q&A response |
| TS-05 | Inbox Bid Detection | WF-006 → bid email detected → bid_entries row created |
| TS-06 | New Project Setup | WF-001 → project row in Postgres → Qdrant seed → project visible in dashboard |
| TS-07 | Drive Sync | WF-SYNC-DRIVE → drive_memory vectors written → Project Brain Q&A returns doc context |
| TS-08 | PM Weekly Report | WF-PM-W → synthesizes all services → email delivered |
| TS-09 | Executive Health Report | WF-REPORT-EXEC → all 4 projects → health badges correct → email delivered |

---

## §17.5 Production Status Lifecycle (9 Values)

Every workflow, service, and infrastructure component carries exactly one of these status values at all times. The value reflects the highest gate it has passed, with documented evidence.

| # | Status Value | Meaning |
|---|-------------|---------|
| 1 | Not Started | Not yet built |
| 2 | Built - Untested | Code exists and runs; no formal test evidence |
| 3 | Testing | Actively being tested; evidence being collected |
| 4 | Failed Validation | Test run produced failures; defect logged |
| 5 | Validated in Test | Passed engineering or integration validation; evidence documented |
| 6 | UAT Ready | Passed Gate 1-3; ready for Buck to run real scenarios |
| 7 | UAT Passed | Buck confirmed the output is correct and useful |
| 8 | Pilot Ready | Cleared for live use on one real project |
| 9 | Production Ready | All 5 gates passed; Buck signed off; cleared for all projects |

**Rule:** Status can only advance when evidence is documented in `docs/TEST_RESULTS.md`. Status must be downgraded to "Failed Validation" any time a defect is found that invalidates prior test evidence.

---

## §17.6 Validation Gate 1 — Engineering Validation

**Who runs it:** Claude Code  
**Evidence stored in:** `docs/TEST_RESULTS.md` — Gate 1 section  
**Pass criteria:** All checks below pass with no P0/P1 defects open

### Checklist

| # | Check | Method |
|---|-------|--------|
| EV-01 | All 90+ API endpoints return correct HTTP status on happy path (200/201) | `curl` or pytest |
| EV-02 | Auth enforcement: every `/api/v1/*` endpoint returns 401 without X-API-Key | `curl` without header |
| EV-03 | DB write round-trip: POST → verify row in Postgres | SELECT after each write |
| EV-04 | Qdrant write round-trip: embed → upsert → search returns result | Search after each upsert |
| EV-05 | Error handling: malformed input returns 422; missing required fields documented | `curl` with bad payload |
| EV-06 | No 500 errors on documented happy path for any service | Test all 9 services |
| EV-07 | HubSpot sync: deals page, notes, contacts sync without error | Run sync_hubspot.py |
| EV-08 | Drive sync: files processed, drive_memory count increases | Run sync_drive.py |
| EV-09 | All 18 workflows trigger without 500 | POST /api/v1/workflows/{id}/trigger |
| EV-10 | Backup script completes: pg_dump file written, Qdrant snapshot created | Run backup.sh |
| EV-11 | Monitor script completes: health checks pass, no false alerts | Run monitor.sh once |
| EV-12 | Dashboard loads: all 6 panel fetch calls return 200 | Browser or curl |

---

## §17.7 Validation Gate 2 — Integration Testing

**Who runs it:** Claude Code  
**Evidence stored in:** `docs/TEST_RESULTS.md` — Gate 2 section  
**Pass criteria:** All 9 test scenarios complete end-to-end with verified output

### Service→DB→Qdrant Chains

| # | Chain | Verification |
|---|-------|-------------|
| IT-01 | WF-SUPER → daily_logs → project_memory | Row in daily_logs; vector in project_memory |
| IT-02 | WF-SUPER → schedule_variance | analyze_log() produces schedule_variance row |
| IT-03 | WF-006 → bid_entries | bid email detected; amount extracted; row in bid_entries |
| IT-04 | WF-SYNC-HS → hubspot_deals, hubspot_notes | Count matches HubSpot source |
| IT-05 | WF-SYNC-DRIVE → drive_memory | Vector count increases after sync |
| IT-06 | WF-001 → projects + project_memory | Project row + Qdrant seed vector confirmed |
| IT-07 | project-brain Q&A → useful synthesis | Query returns structured data citing real project facts |
| IT-08 | bid-intelligence → leveling summary | Returns coverage %, unleveled trades, risk flags |
| IT-09 | WF-REPORT-DAILY → email | Email received at buck@ahmaspen.com within 60 seconds of trigger |

---

## §17.8 Validation Gate 3 — Workflow Acceptance Testing (WAT)

**Who runs it:** Claude Code (execution); Buck Adams (output review)  
**Evidence stored in:** `docs/WORKFLOW_TEST_MATRIX.md` (result column)  
**Pass criteria:** All 18 workflows have documented test result; no P0/P1 defects; outputs are correct

Every workflow in `docs/WORKFLOW_TEST_MATRIX.md` must advance from "Built - Untested" to "Validated in Test" or higher. Any that fail must be logged as defects in `docs/KNOWN_ISSUES.md`.

---

## §17.9 Validation Gate 4 — User Acceptance Testing (UAT)

**Who runs it:** Buck Adams  
**Evidence stored in:** `docs/UAT_RESULTS.md`  
**Pass criteria:** Buck confirms all Tier 1 UAT scenarios produce useful, correct, business-appropriate output

### UAT Principles
- UAT uses real project data, not test data
- Buck triggers each workflow manually and reviews the output
- Outputs are evaluated on usefulness to Buck's real work — not just technical correctness
- Any output that is confusing, incorrect, or not useful is a UAT defect regardless of technical correctness

### UAT Scenarios (Tier 1 — Required for go-live)

| # | Scenario | Buck's Evaluation Criteria |
|---|----------|-----------------------------|
| UAT-01 | Submit a real daily log for 101 Francis or 64 Eastwood | Log saved; field report email is correct and useful |
| UAT-02 | Ask Project Brain a real question about 1355 Riverside | Answer is accurate and cites real bid/risk data |
| UAT-03 | Run morning brief | Email has correct project status; readable in under 2 minutes |
| UAT-04 | Review exec health report | Health badges reflect actual project reality |
| UAT-05 | Submit a real meeting note | Meeting saved; action items extractable |

### UAT Scenarios (Tier 2 — Required before full production rollout)

| # | Scenario |
|---|----------|
| UAT-06 | Bid email arrives; WF-006 detects it; bid_entries row is correct |
| UAT-07 | PM daily review runs; synthesis is useful for Buck's 5-minute daily check |
| UAT-08 | Drive sync runs after adding a new document; Project Brain can reference it |
| UAT-09 | Risk intelligence flags a real constraint from a daily log |
| UAT-10 | Weekly PM report email is comprehensive enough to replace a manual status meeting |

---

## §17.10 Validation Gate 5 — Pilot Approval and Go-Live Authorization

**Who runs it:** Buck Adams (approval); Claude Code (documentation)  
**Evidence stored in:** `docs/PILOT_READINESS_REPORT.md`  
**Pass criteria:** Buck explicitly approves; `docs/PILOT_READINESS_REPORT.md` signed off

### Pilot definition
- One active project runs through the system for 5 consecutive business days
- All daily logs submitted via WF-SUPER
- Morning brief reviewed each day
- No P0 or P1 defects arise
- Backup confirmed to be running

### Go-live authorization
Buck Adams must state: **"I approve go-live for [project(s)]."** This statement is recorded in `docs/PILOT_READINESS_REPORT.md`. Until this happens, the system status is BLOCKED.

---

## §17.11 Defect Classification and Logging

All defects are logged in `docs/KNOWN_ISSUES.md`. Every defect has:
- Unique ID: `KI-NNN`
- Severity: P0 / P1 / P2 / P3
- Component affected
- Description of failure
- Steps to reproduce
- Impact on production readiness
- Status: Open / In Progress / Resolved
- Resolution date

### Severity Definitions

| Severity | Definition | Go-live Impact |
|----------|------------|---------------|
| P0 | Data corruption, security breach, or complete system failure | Hard blocker — cannot go live |
| P1 | Workflow fails on documented happy path; report email not delivered; wrong data written to DB | Hard blocker — must fix before advancing gate |
| P2 | Feature degrades but workaround exists; non-critical data missing | Soft blocker — must fix before UAT |
| P3 | Cosmetic, logging gap, or minor data quality issue | Not a blocker; backlog |

---

## §17.12 Regression Policy

Every time code is changed in `03_Source_Code/` or `infrastructure/`, the following regression checks must run:

1. API health check: `GET /health` returns 200
2. Auth check: `GET /api/v1/projects` without key returns 401; with key returns 200
3. Dashboard load: `/dashboard` loads without JS errors
4. WF-SUPER smoke: POST to `/api/v1/workflows/wf-super/daily-log` with test payload returns 200
5. DB connectivity: `SELECT count(*) FROM projects` returns 4

For major changes (new service, schema change, new workflow), the relevant gate(s) must be re-run and evidence updated.

---

## §17.13 Documentation Evidence Requirements

The following documentation must exist and be current before each gate can be declared passed:

| Gate | Required Documents |
|------|-------------------|
| Gate 1 | `docs/TEST_RESULTS.md` with Gate 1 section complete |
| Gate 2 | `docs/TEST_RESULTS.md` with Gate 2 section complete; `docs/SYSTEM_DATA_FLOW.md` current |
| Gate 3 | `docs/WORKFLOW_TEST_MATRIX.md` with result column filled for all 18 workflows |
| Gate 4 | `docs/UAT_PLAN.md` + `docs/UAT_RESULTS.md` with Buck's sign-off |
| Gate 5 | `docs/PILOT_READINESS_REPORT.md` with 5-day pilot evidence + Buck's explicit approval |

---

## §17.14 Rollback Procedures

See `docs/ROLLBACK_PLAN.md` for detailed procedures. Summary:

| Scenario | Procedure |
|----------|-----------|
| API failure after code change | `launchctl stop com.hci.api` → `git revert` → `launchctl start com.hci.api` |
| Schema migration failure | Restore from most recent pg_dump backup; run `infrastructure/postgres/init.sql` |
| Qdrant data corruption | Restore from most recent Qdrant snapshot (in HCI_Backups) |
| Docker service failure | `docker compose down && docker compose up -d` from `infrastructure/` |
| Workflow logic regression | Revert specific workflow file via git; restart API |

Rollback must always be tested in `docs/ROLLBACK_PLAN.md` as part of Gate 1.

---

## §17.15 UAT Process

Full UAT process is defined in `docs/UAT_PLAN.md`. The process steps:

1. Gates 1-3 declared passed with documented evidence
2. Claude Code marks all Tier 1 workflows as "UAT Ready" in `docs/WORKFLOW_TEST_MATRIX.md`
3. Buck is briefed: which scenarios to run, what to evaluate, where to give feedback
4. Buck runs Tier 1 scenarios over 1-2 business days
5. All feedback is logged as UAT defects or approvals in `docs/UAT_RESULTS.md`
6. P0/P1 UAT defects are fixed; Buck re-runs affected scenarios
7. Buck declares UAT passed per scenario
8. Claude Code updates `docs/UAT_RESULTS.md` and advances status to "UAT Passed"

---

## §17.16 Production Readiness Criteria

The system (or a component) is **Production Ready** when:

1. All 5 validation gates are documented as passed
2. No P0 or P1 defects are open
3. Backup has completed at least one successful run (verified in backup log)
4. Monitor is running and has sent at least one test alert to buck@ahmaspen.com
5. `docs/PILOT_READINESS_REPORT.md` exists and contains Buck's explicit go-live approval
6. `docs/PRODUCTION_READINESS_CHECKLIST.md` reflects current reality (not Phase 12 snapshot)

---

## §17.17 Testing Tools and Infrastructure

| Tool | Use | Location |
|------|-----|----------|
| curl | API endpoint testing | System (Bash) |
| pytest | Unit + API tests (build out in 15_Tests/) | `15_Tests/` |
| Python scripts | DB integration tests, workflow smoke tests | `03_Source_Code/workflows/` |
| Playwright | UI/email tests (existing, used for Houzz) | `03_Source_Code/workflows/sync_houzz.py` |
| Qdrant HTTP API | Vector store verification | Direct API calls |
| PostgreSQL client | DB query verification | `psql` via Bash |
| backup.sh | Backup verification | `03_Source_Code/scripts/backup.sh` |
| monitor.sh | Monitor verification | `03_Source_Code/scripts/monitor.sh` |

---

## §17.18 QA Calendar and Cadence

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Regression smoke test | Every code change | Claude Code |
| Gate 1 Engineering Validation | Once (then on major changes) | Claude Code |
| Gate 2 Integration Testing | Once (then on major changes) | Claude Code |
| Gate 3 Workflow Acceptance | Once per workflow per major change | Claude Code |
| Gate 4 UAT | Once (then on significant feature changes) | Buck Adams |
| Gate 5 Pilot | Once per go-live authorization | Buck Adams |
| Known Issues review | Each session | Claude Code |
| TEST_RESULTS.md update | After any test run | Claude Code |
| PRODUCTION_READINESS_CHECKLIST.md update | After any gate advance | Claude Code |

---

## §17.19 Governance

- **Production go-live is BLOCKED until all 5 gates pass and Buck explicitly approves.**
- This volume (BOOK_00 §17) is the authoritative source for QA process.
- `docs/QA_VALIDATION_STANDARD.md` is the operational reference (shorter, procedural).
- Any deviation from this process requires Buck Adams's explicit approval and a note in `AI_TEAM/03_DECISIONS.md`.
- Claude Code must not mark any component "Production Ready" without documented evidence.
- "It worked when I built it" is not test evidence.
