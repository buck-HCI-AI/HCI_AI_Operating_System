# HCI AI — Implementation Risk Register
**Date:** 2026-06-25 | **Audit:** Master Validation v1.0  
**Format:** ID | Probability | Impact | Risk | Mitigation

---

## RISK-001 — Mac mini Migration DB Init Failure
**Probability:** HIGH (was certain if unfixed)  
**Impact:** CRITICAL  
**Status:** ✅ MITIGATED (GAP-002 fixed; init.sql now complete)  
**Risk:** Fresh Docker start on Mac mini would create 14-table DB; 8 tables missing; WF-SUPER, WF-PM, and all Phase 8-11 workflows would crash on first run.  
**Mitigation Applied:** init.sql updated with all 22 tables. Also: setup_mac_mini.sh Step 9 restores from pg_dump, which includes all tables regardless of init.sql.  
**Residual Risk:** LOW — pg_dump restore is the primary migration path; init.sql is secondary (new/clean installs only).

---

## RISK-002 — Credential Rotation Breaks 7 Workflows
**Probability:** HIGH (was certain if unfixed)  
**Impact:** HIGH  
**Status:** ✅ MITIGATED (GAP-001 fixed)  
**Risk:** 7 workflow files used hardcoded `password="hci_postgres_2026"`. Any password change (e.g., during Mac mini setup, security rotation) would silently break all 7 workflows while newer workflows (WF-SUPER, WF-PM, WF-004, WF-006) continued working. Debugging would be difficult.  
**Mitigation Applied:** All 7 files now read `POSTGRES_PASSWORD` from environment.  
**Residual Risk:** NONE.

---

## RISK-003 — Schedule Intelligence Blind Without Houzz Baseline
**Probability:** CERTAIN (Houzz tables missing from live DB)  
**Impact:** MEDIUM  
**Status:** OPEN — see GAP-004  
**Risk:** ScheduleIntelligenceService.analyze_log() compares field logs against "Known schedule items" but the houzz_schedule_items table is missing. Claude gets "No schedule items on file" and can only produce generic variance analysis, not activity-level detection.  
**Mitigation:** Guard clause in ScheduleIntelligenceService prevents a crash. System degrades gracefully.  
**Resolution Path:** Run Houzz table migration SQL, then run WF-SYNC-HOUZZ to populate schedule baseline.  
**Residual Risk:** MEDIUM until Houzz tables are created.

---

## RISK-004 — Project Brain Q&A Quality Degraded by Empty Qdrant Collections
**Probability:** CERTAIN (drive_memory = 0 vectors)  
**Impact:** MEDIUM  
**Status:** OPEN — see GAP-005  
**Risk:** Project Brain Q&A searches 5 Qdrant collections (drive_memory, project_memory, bid_memory, vendor_memory, lessons_learned). drive_memory is empty, vendor_memory is empty. Q&A answers lack document and vendor context — the primary intelligence value proposition.  
**Mitigation:** System returns "no relevant documents found" rather than hallucinating. Project Brain still returns structured Postgres data (bids, deals, logs).  
**Resolution Path:** Re-run Drive sync; build vendor embed pipeline.  
**Residual Risk:** MEDIUM until collections are populated.

---

## RISK-005 — Document Uploads Silently Failed (Now Fixed)
**Probability:** CERTAIN (was happening before this audit)  
**Impact:** HIGH  
**Status:** ✅ MITIGATED (GAP-003 fixed)  
**Risk:** `hci_project_documents` Qdrant collection did not exist. Every document uploaded via `POST /api/v1/services/document-intelligence/upload` would succeed in MinIO but fail at Stage 4 (Qdrant upsert). The error was caught (`result["index_error"] = str(e)`) but the upload appeared "successful" with 0 chunks indexed. Documents were stored but not searchable.  
**Mitigation Applied:** All 5 missing Qdrant collections created.  
**Residual Risk:** LOW — any documents uploaded before this audit are in MinIO but not indexed. Re-ingest if needed.

---

## RISK-006 — WF-PM sys.path Manipulation Fragility
**Probability:** LOW  
**Impact:** MEDIUM  
**Status:** OPEN  
**Risk:** wf_pm.py uses `sys.path.insert()` at module level to import from 5 different service directories. Any directory rename, file rename, or import order change silently breaks the PM workflow. Already caused issues during development (ScheduleIntelligenceService import in WF-SUPER).  
**Mitigation:** Each import is wrapped in try/except; failure returns `{"error": str(e)}` not a crash. PM review continues with partial data.  
**Resolution Path:** Long-term: refactor to a proper package structure with `__init__.py` and installed via pip. Short-term: acceptable.  
**Residual Risk:** LOW for now; MEDIUM after Mac mini migration if paths differ.

---

## RISK-007 — No Automated Tests
**Probability:** N/A (it's a fact, not a probability)  
**Impact:** MEDIUM (cumulative)  
**Status:** OPEN — see GAP-012  
**Risk:** 18 workflows and 9 services have zero automated tests. Any refactor, dependency update, or schema change can introduce regressions that are only caught in production. The WF-SUPER pipeline is particularly complex (9 stages) and a failure in Stage 4 (schedule analysis) silently continues.  
**Mitigation:** Manual testing after each session. Monitoring script catches API-down scenarios.  
**Resolution Path:** Phase 12 — build smoke tests for critical path (WF-SUPER → email; Project Brain Q&A; auth).  
**Residual Risk:** MEDIUM ongoing.

---

## RISK-008 — Qdrant "Unhealthy" Docker Status
**Probability:** N/A (current state)  
**Impact:** LOW  
**Status:** OPEN (monitoring)  
**Risk:** `docker ps` shows hci_qdrant as "unhealthy" despite the Qdrant API responding correctly. The healthcheck in docker-compose.yml may be checking an endpoint that doesn't exist or requires a different response format. On restart or drive watcher trigger, the unhealthy status may prevent dependent containers from starting.  
**Mitigation:** API is functional. Collections respond. Backup/restore works.  
**Resolution Path:** Update Qdrant healthcheck in docker-compose.yml: `test: ["CMD", "curl", "-f", "http://localhost:6333/readyz"]`  
**Residual Risk:** LOW.

---

## Risk Summary

| ID | Probability | Impact | Status |
|----|------------|--------|--------|
| RISK-001 Mac mini DB init | ~~HIGH~~ | ~~CRITICAL~~ | ✅ MITIGATED |
| RISK-002 Credential rotation | ~~HIGH~~ | ~~HIGH~~ | ✅ MITIGATED |
| RISK-003 Schedule baseline | CERTAIN | MEDIUM | OPEN |
| RISK-004 Qdrant empty collections | CERTAIN | MEDIUM | OPEN |
| RISK-005 Document upload silent fail | ~~CERTAIN~~ | ~~HIGH~~ | ✅ MITIGATED |
| RISK-006 sys.path fragility | LOW | MEDIUM | OPEN |
| RISK-007 No tests | N/A | MEDIUM | OPEN |
| RISK-008 Qdrant unhealthy status | N/A | LOW | OPEN |

**3 of 8 risks fully mitigated in this audit.**
