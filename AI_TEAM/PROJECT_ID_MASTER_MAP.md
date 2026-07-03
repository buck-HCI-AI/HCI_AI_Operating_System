# PROJECT_ID MASTER MAP
**Verified:** 2026-07-02 by Browser Claude from gateway
**ARB catch:** GBT flagged project_id mismatch in CYCLE40 — corrected here

## AUTHORITATIVE PROJECT ID MAPPING

| project_code | project_name | project_id | Notes |
|---|---|---|---|
| 64EW | 64 Eastwood | 1 | |
| 101F | 101 Francis | 2 | |
| 1355R | 1355 Riverside | 3 | |
| 246GW | 246 Gallo Way | 8 | |
| QATEST | QA Sandbox | 28 | NEVER use in production queries |

## CORRECTION TO CYCLE40

CYCLE40_TEST_DATA_ISOLATION_ENFORCEMENT.md incorrectly stated project_id=8 for 101F.

**CORRECT:** 101F = project_id=**2**
**WRONG (in CYCLE40 spec):** project_id=8 (that is 246GW)

Code has been notified via ai_messages 280 (BC) and 281 (GBT).

## SQL CORRECTION FOR 101F CLEANUP

```sql
-- CORRECT: Use project_id=2 for 101F
SELECT id, project_id, record_type, title, created_at
FROM project_events
WHERE project_id = 2
  AND (
      title ILIKE '%[TEST]%'
          OR title ILIKE '%[DEFERRED]%'
              OR title ILIKE '%DRAFT%'
                  OR title ILIKE '%placeholder%'
                      OR title ILIKE '%CSI Division%'
                        )
                        ORDER BY created_at;

                        -- Run dry-run SELECT first, report count to BC before executing UPDATE/DELETE
                        ```

                        ## RULES

                        1. ALWAYS use project_code (101F, 1355R, etc.) in gateway API calls
                        2. ALWAYS use project_id (integer) in direct SQL queries
                        3. NEVER assume project_id from sequential numbering
                        4. Verify from this file before any destructive DB operation
                        5. QATEST (project_id=28) excluded from ALL production queries

                        ---

                        *Verified by BC 2026-07-02 from /gateway/project/{code}/brain responses*
                        *GBT ARB watch item #1 resolved*
