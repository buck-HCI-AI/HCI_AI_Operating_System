# HCI AI — Gap Register
**Date:** 2026-06-25 | **Audit:** Master Validation v1.0  
**Format:** ID | Severity | Area | Description | Status | Fix

---

## CRITICAL (P0) — System-breaking if not addressed

### GAP-001 — Hardcoded DB Credentials
**Severity:** CRITICAL  
**Area:** Workflow Layer  
**Files:** wf001_new_project.py, wf002_meeting_intelligence.py, wf003_morning_brief.py, wf005_lessons_learned.py, sync_hubspot.py, sync_houzz.py, sync_drive.py  
**Description:** 7 workflow/sync files had DB connection dicts with hardcoded password `hci_postgres_2026` instead of reading from .env. Would break silently on Mac mini migration if password changes.  
**Status:** ✅ FIXED (this audit)  
**Fix Applied:** All 7 files now use `os.environ.get("POSTGRES_PASSWORD", "")` with dotenv load.

---

### GAP-002 — init.sql Missing 8 Tables + daily_logs Columns
**Severity:** CRITICAL  
**Area:** Database / Infrastructure  
**Files:** infrastructure/postgres/init.sql  
**Description:** Fresh `docker compose up` creates only 14 of 22 tables. Missing: long_lead_items, procurement_items, risks, historical_cost_records, workflow_events, schedule_variance, rfis, submittals. Also missing 9 daily_logs columns added in Phase 9 (manpower, deliveries, inspections, quality_notes, safety_notes, subcontractor_progress, constraints, lookahead, field_risks).  
**Status:** ✅ FIXED (this audit)  
**Fix Applied:** init.sql updated with all 22 table definitions and all daily_logs columns.

---

### GAP-003 — hci_project_documents Qdrant Collection Missing
**Severity:** CRITICAL  
**Area:** Vector Store / Ingestion  
**Description:** The ingestion pipeline (`ingest.py`) routes documents to `hci_project_documents` collection. Collection did not exist. Every document upload via API would succeed in MinIO but fail silently at Qdrant upsert stage. Also missing: hci_sops, hci_historical_costs, hci_procurement, hci_vendor_intelligence.  
**Status:** ✅ FIXED (this audit)  
**Fix Applied:** All 5 missing Qdrant collections created (384-dim, Cosine distance).

---

## HIGH (P1) — Degraded functionality or migration risk

### GAP-004 — Houzz Tables Missing from Live DB
**Severity:** HIGH  
**Area:** Database / Houzz Integration  
**Tables:** houzz_projects, houzz_daily_logs, houzz_schedule_items  
**Description:** These 3 tables were defined in init.sql but did not exist in the live DB. Created via inline CREATE TABLE IF NOT EXISTS statements.  
**Status:** ✅ FIXED (2026-06-25)  
**Fix Applied:** All 3 tables created directly in live DB. Live DB now has 22 tables matching init.sql.

---

### GAP-005 — vendor_memory and drive_memory Qdrant Collections Empty
**Severity:** HIGH  
**Area:** Data Enrichment / Vector Store  
**Description:** `vendor_memory` has no vectors despite 392 vendors in Postgres. `drive_memory` reports 0 vectors despite Drive sync having run. Project Brain Q&A returns no vendor or document context from Qdrant, significantly degrading intelligence quality.  
**Status:** OPEN  
**Fix:**  
1. Re-run `POST /api/v1/workflows/sync/drive` to repopulate drive_memory  
2. Build vendor embed pipeline: read vendors table → embed → upsert vendor_memory  
**Impact:** Project Brain Q&A lacks vendor and document context.

---

### GAP-006 — 05_Database/schema.sql Out of Date
**Severity:** HIGH  
**Area:** Documentation / Schema Governance  
**Files:** 05_Database/postgres/schema.sql  
**Description:** This file is the documented "source of truth" per init.sql header, but it only contains the original 14-table Phase 1 schema. Developers or the Mac mini setup might use this file and get an incomplete database.  
**Status:** OPEN  
**Fix:** Copy updated init.sql content to 05_Database/schema.sql (or symlink).  
**Impact:** Schema documentation mismatch; fresh setup risk.

---

### GAP-007 — WF-003 Email Address Hardcoded
**Severity:** HIGH (now FIXED)  
**Area:** Workflow / Configuration  
**File:** wf003_morning_brief.py  
**Description:** `BUCK_EMAIL` was hardcoded to `("Buck Adams", "buck@hendricksoninc.com")` — not @ahmaspen.com. Morning brief emails would go to wrong address.  
**Status:** ✅ FIXED (this audit)  
**Fix Applied:** Now reads `os.environ.get("BUCK_EMAIL", "buck@ahmaspen.com")`.

---

## MEDIUM (P2) — Incomplete functionality, manageable now

### GAP-008 — WF-001, WF-002, WF-005, WF-006 Do Not Write workflow_events
**Severity:** MEDIUM  
**Area:** Workflow Audit Trail  
**Description:** Four workflows run successfully but do not write to `workflow_events`. New project creation (WF-001), meeting logging (WF-002), lessons learned (WF-005), and inbox review (WF-006) leave no audit trail.  
**Status:** OPEN  
**Impact:** Incomplete workflow history; workflow traceability matrix shows gaps.  
**Fix:** Add `_log_workflow_event()` calls to each workflow at start and completion.

---

### GAP-009 — No Launchd Schedule for WF-PM Daily Review or Exec Health Report
**Severity:** MEDIUM  
**Area:** Automation  
**Description:** WF-PM daily review and the executive health report have no launchd agent scheduled. They must be manually triggered. WF-PM-W (weekly) and WF-003 (morning brief) are scheduled but the daily PM review is not.  
**Status:** OPEN  
**Impact:** PM oversight depends on manual trigger; no automated daily health reporting.  
**Fix:** Add launchd plist for WF-PM daily review (e.g., 5 PM daily) and exec health report (Friday 4 PM).

---

### GAP-010 — Empty Operational Tables
**Severity:** MEDIUM  
**Area:** Data Enrichment  
**Tables:** meetings (0), rfis (0), submittals (0), long_lead_items (0), procurement_items (0), hubspot_notes (0), hubspot_tasks (0)  
**Description:** Seven tables are empty because the system has not been used in production yet. Intelligence services that query these tables return empty results, reducing Project Brain answer quality.  
**Status:** OPEN (expected — system recently deployed)  
**Impact:** Intelligence quality improves with real operational data.  
**Fix:** Begin active use: submit daily logs via WF-SUPER, log meetings via WF-002, let WF-006 inbox review run daily.

---

## LOW (P3) — Minor / polish

### GAP-011 — wf_superintendent.py Stage 2: Double-Write to crew_on_site and manpower
**Severity:** LOW  
**Area:** Workflow Bug  
**File:** wf_superintendent.py (Stage 2 INSERT)  
**Description:** The INSERT writes `json.dumps(crew_on_site)` to both the `crew_on_site` column and the `manpower` column. The `manpower` column was intended for headcount data (different from crew names). Harmless but semantically incorrect.  
**Status:** OPEN  
**Fix:** Pass separate `manpower` parameter or derive headcount from crew_on_site list length.

---

### GAP-012 — No Automated Test Suite
**Severity:** LOW  
**Area:** Testing  
**Directory:** 15_Tests/ (empty)  
**Description:** Zero automated tests. No unit tests, integration tests, or API smoke tests. Regressions across 18 workflows and 9 services go undetected until production failure.  
**Status:** OPEN  
**Fix:** Build smoke tests for critical paths: WF-SUPER → schedule_variance → report chain; Project Brain snapshot; auth enforcement.

---

### GAP-013 — 10_Agents/ and 11_Prompts/ Are Empty Placeholders
**Severity:** LOW  
**Area:** Future Architecture  
**Description:** 6 agent directories (bid_agent, executive_agent, etc.) and 11_Prompts/ contain no code or prompts. These are Phase 12+ features.  
**Status:** OPEN (expected)  
**Impact:** None currently. Document as planned work.

---

## Summary

| Severity | Count | Fixed This Audit | Open |
|----------|-------|-----------------|------|
| CRITICAL | 3 | 3 | 0 |
| HIGH | 4 | 1 | 3 |
| MEDIUM | 3 | 0 | 3 |
| LOW | 3 | 0 | 3 |
| **Total** | **13** | **4** | **9** |
