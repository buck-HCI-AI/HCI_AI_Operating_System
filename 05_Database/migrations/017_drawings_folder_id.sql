-- Migration 017: Add drawings_folder_id to projects table
-- Added: 2026-06-29 (backfill migration — column was created via ALTER TABLE during session)
-- Purpose: Store Google Drive drawings/plans folder ID per project for direct API access

ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS drawings_folder_id VARCHAR(128);

COMMENT ON COLUMN projects.drawings_folder_id IS
    'Google Drive folder ID for the project drawings/plans folder (04_Drawings)';

-- Known values as of 2026-06-29
UPDATE projects SET drawings_folder_id = '1RCjDr2_A0mYVFlqF_aPiGLMjNyv_oUU0' WHERE project_code = '64EW';
UPDATE projects SET drawings_folder_id = '1VELmjPJ4n2KLPo-VaqTKWCjvMbTRfISSH' WHERE project_code = '101F';
-- 1355R and 246GW drawings_folder_id TBD — must be populated when Drive folder IDs are confirmed
