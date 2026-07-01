-- Migration 019: AI Messages — P0 reconciliation against ChatGPT Chief Architect spec
-- ("Code communication ai" directive, 2026-06-30). Two directives now agree on
-- RECEIVED/FAILED over ACKNOWLEDGED/REJECTED, and on source_agent/target_agent
-- naming, next_action_owner, related_approval_id. Reconciling rather than forking
-- a second table.

ALTER TABLE ai_messages RENAME COLUMN source TO source_agent;
ALTER TABLE ai_messages RENAME COLUMN target TO target_agent;

ALTER TABLE ai_messages ADD COLUMN IF NOT EXISTS next_action_owner   VARCHAR(50);
ALTER TABLE ai_messages ADD COLUMN IF NOT EXISTS related_approval_id INTEGER;

-- Status vocabulary reconciliation: ACKNOWLEDGED -> RECEIVED, REJECTED -> FAILED
UPDATE ai_messages SET status = 'RECEIVED' WHERE status = 'ACKNOWLEDGED';
UPDATE ai_messages SET status = 'FAILED'   WHERE status = 'REJECTED';

ALTER TABLE ai_messages DROP CONSTRAINT IF EXISTS ai_messages_status_chk;
ALTER TABLE ai_messages ADD CONSTRAINT ai_messages_status_chk CHECK (status IN
    ('NEW','RECEIVED','IN_PROGRESS','BLOCKED','COMPLETE','NEEDS_BUCK_APPROVAL','FAILED','STALE'));

COMMENT ON COLUMN ai_messages.next_action_owner IS
    'Who needs to act next: buck|chatgpt|claude_code|browser_claude|n8n|none';
COMMENT ON COLUMN ai_messages.related_approval_id IS
    'FK-by-convention to approval_queue.id when this message tracks an external-write approval';
