-- Houzz Import Validation Routines
-- Sprint 2.5 Platform Hardening | Chief Architect Directive 2026-06-27
-- Run after each Browser Claude extraction to verify data integrity.
-- All queries are READ-ONLY — no writes.

-- ── 1. DUPLICATE DAILY LOGS ────────────────────────────────────────────────
-- Finds logs with same project + date (should be unique per project per day)
SELECT 'duplicate_daily_logs' as check_name,
       project_id, log_date, COUNT(*) as duplicate_count
FROM houzz_daily_logs
GROUP BY project_id, log_date
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- ── 2. DUPLICATE SCHEDULE ITEMS ───────────────────────────────────────────
-- Finds items with same activity_id (primary key constraint should catch, but verify)
SELECT 'duplicate_schedule_items' as check_name,
       activity_id, COUNT(*) as duplicate_count
FROM project_schedule_items
GROUP BY activity_id
HAVING COUNT(*) > 1;

-- ── 3. ORPHAN RECORDS (project_id references nothing) ─────────────────────
SELECT 'orphan_daily_logs' as check_name, COUNT(*) as orphan_count
FROM houzz_daily_logs dl
WHERE dl.project_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM houzz_projects hp WHERE hp.houzz_project_id = dl.project_id);

SELECT 'orphan_schedule_items' as check_name, COUNT(*) as orphan_count
FROM project_schedule_items si
WHERE si.project_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM houzz_projects hp WHERE hp.houzz_project_id = si.project_id);

-- ── 4. INVALID TIMESTAMPS ─────────────────────────────────────────────────
SELECT 'future_log_dates' as check_name, COUNT(*) as invalid_count
FROM houzz_daily_logs
WHERE log_date > CURRENT_DATE;

SELECT 'future_schedule_dates' as check_name, COUNT(*) as invalid_count
FROM project_schedule_items
WHERE start_date > end_date AND end_date IS NOT NULL;

SELECT 'old_timestamps' as check_name, COUNT(*) as invalid_count
FROM houzz_daily_logs
WHERE log_date < '2020-01-01';

-- ── 5. MISSING PROJECT IDs ────────────────────────────────────────────────
SELECT 'logs_missing_project_id' as check_name, COUNT(*) as missing_count
FROM houzz_daily_logs WHERE project_id IS NULL;

SELECT 'schedule_missing_project_id' as check_name, COUNT(*) as missing_count
FROM project_schedule_items WHERE project_id IS NULL;

-- ── 6. ROW COUNT SUMMARY (run after extraction) ───────────────────────────
SELECT 'row_counts' as check_name,
       (SELECT COUNT(*) FROM houzz_projects) as projects,
       (SELECT COUNT(*) FROM houzz_daily_logs) as daily_logs,
       (SELECT COUNT(*) FROM project_schedule_items) as schedule_items;

-- ── 7. COMPLETENESS CHECK (projects with no logs) ─────────────────────────
SELECT 'projects_without_logs' as check_name, hp.name, hp.houzz_project_id
FROM houzz_projects hp
WHERE NOT EXISTS (
    SELECT 1 FROM houzz_daily_logs dl WHERE dl.project_id = hp.houzz_project_id
);

-- ── 8. SCHEDULE HIERARCHY VALIDATION ─────────────────────────────────────
-- Child items should reference existing parent items
SELECT 'orphan_child_tasks' as check_name, COUNT(*) as orphan_count
FROM project_schedule_items child
WHERE child.parent_item_id IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM project_schedule_items parent
      WHERE parent.activity_id = child.parent_item_id
  );
