# CYCLE 40 — Test Data Isolation Enforcement
**GBT Cycle:** 40
**Sprint:** 8
**Priority:** P0 — Data Integrity
**Status:** SPEC + CLEANUP REQUIRED
**Date:** 2026-07-02
**Author:** Browser Claude (BC)

---

## Incident Report

**Incident:** Test data contaminating live production project 101 Francis (project_id=8, code=101F)
**Detected:** 2026-07-02 by BC during mission control audit
**Impact:** Gateway /brain endpoint returning test records as real project intelligence

### Contaminated Records Identified in 101F
1. [TEST] Gate 3 meeting placeholder entry
2. [DEFERRED] Defer test decision (EXEC-D5C0CFC)
3. DRAFT bid package row
4. Subcontractor/CSI Division placeholder row

---

## ADR-S8-002: Test Data Isolation (PERMANENT)

**Decision:** All test inserts MUST use project_id=28 (QATEST sandbox). No exceptions.

**Rationale:**
- Test records in live projects corrupt AI intelligence responses
- Field GPTs and Management GPTs read /brain endpoint as source of truth
- Superintendent decisions made on corrupted data = field risk
- One contaminated record can cascade into wrong schedule, cost, or risk assessments

**Rule:** Enforce at application layer, not just by convention.

---

## Immediate Cleanup Required (Code Action)

Code to execute the following against the production database:

```sql
-- Step 1: Identify all test records in live projects (1-4, 8)
-- Run this first to audit scope
SELECT id, project_id, record_type, title, created_at
FROM project_events
WHERE project_id IN (1, 2, 3, 4, 8)
  AND (
      title ILIKE '%[TEST]%'
          OR title ILIKE '%[DEFERRED]%'
              OR title ILIKE '%DRAFT%'
                  OR title ILIKE '%placeholder%'
                      OR title ILIKE '%CSI Division%'
                        )
                        ORDER BY project_id, created_at;

                        -- Step 2: Move to QATEST (project_id=28) or delete
                        -- DELETE only after confirming records are test artifacts
                        -- Update project_id to 28 if data should be preserved for testing
                        UPDATE project_events
                        SET project_id = 28
                        WHERE project_id = 8
                          AND (
                              title ILIKE '%[TEST]%'
                                  OR title ILIKE '%[DEFERRED]%'
                                      OR (title ILIKE '%DRAFT%' AND title ILIKE '%placeholder%')
                                        );

                                        -- Step 3: Verify 101F is clean
                                        SELECT COUNT(*) FROM project_events
                                        WHERE project_id = 8
                                          AND title ILIKE '%[TEST]%';
                                          -- Expected: 0
                                          ```

                                          **Post-cleanup:** Call GET /gateway/project/101F/brain and confirm no test records in response.

                                          ---

                                          ## Application-Layer Enforcement (Code Build)

                                          Add middleware/validator to prevent future contamination:

                                          ```python
                                          # In service layer (NOT router) — per architecture rules
                                          def validate_project_write(project_id: int, is_test_record: bool = False):
                                              """Enforce test data isolation at write time."""
                                                  LIVE_PROJECT_IDS = {1, 2, 3, 4, 8}  # 101F, 1355R, 64EW, 246GW + others
                                                      TEST_PROJECT_ID = 28  # QATEST sandbox

                                                              if is_test_record and project_id in LIVE_PROJECT_IDS:
                                                                      raise ValueError(
                                                                                  f"Test data cannot be written to live project {project_id}. "
                                                                                              f"Use project_id={TEST_PROJECT_ID} (QATEST) for all test inserts."
                                                                                                      )
                                                                                                          return True
                                                                                                          ```
                                                                                                          
                                                                                                          Alternatively, enforce via DB constraint:
                                                                                                          
                                                                                                          ```sql
                                                                                                          -- Add check constraint on project_events table
                                                                                                          -- Prevents [TEST] or [DEFERRED] prefixes in live projects
                                                                                                          ALTER TABLE project_events
                                                                                                          ADD CONSTRAINT no_test_data_in_live_projects
                                                                                                          CHECK (
                                                                                                            NOT (project_id IN (1, 2, 3, 4, 8) AND title ILIKE '[TEST]%')
                                                                                                            );
                                                                                                            ```
                                                                                                            
                                                                                                            ---
                                                                                                            
                                                                                                            ## Test Isolation Rules (Permanent)
                                                                                                            
                                                                                                            | Rule | Detail |
                                                                                                            |------|--------|
                                                                                                            | Test project | project_id=28 (QATEST) ONLY |
                                                                                                            | Live projects | IDs 1, 2, 3, 4, 8 (and any future active jobs) |
                                                                                                            | Test prefixes | [TEST], [DEFERRED], DRAFT, placeholder |
                                                                                                            | Enforcement | Application layer + optional DB constraint |
                                                                                                            | Portfolio aggregation | QATEST excluded from /portfolio/* endpoints |
                                                                                                            | Brain endpoint | QATEST excluded from /project/{code}/brain |
                                                                                                            
                                                                                                            ---
                                                                                                            
                                                                                                            ## Success Criteria
                                                                                                            
                                                                                                            - [ ] 101F /brain endpoint returns zero test records
                                                                                                            - [ ] SQL cleanup script run and verified
                                                                                                            - [ ] Application-layer validator implemented
                                                                                                            - [ ] All 109 existing tests still pass
                                                                                                            - [ ] QATEST (project_id=28) excluded from portfolio summary
                                                                                                            - [ ] Code posts confirmation to ai_messages when cleanup complete
                                                                                                            
                                                                                                            ---
                                                                                                            
                                                                                                            ## Directive Reference
                                                                                                            
                                                                                                            - Gateway directive posted: request_id f4a73622
                                                                                                            - ADR: ADR-S8-002 (Test Data Isolation — PERMANENT)
                                                                                                            - Incident: 2026-07-02 BC audit of 101F brain
                                                                                                            - Code channel: Post cleanup confirmation to ai_messages
                                                                                                            
                                                                                                            ---
                                                                                                            
                                                                                                            *Generated by Browser Claude — 2026-07-02 — Per never-stop directive*
