# ADR-003: Generic Mining Pipeline

**Status:** Accepted | **Date:** 2026-06-27 | **Author:** Claude Code (Autonomous Development Mode)

## Context

Mining was triggered manually via API calls with no standard lifecycle. Knowledge graph updates and executive intelligence were separate one-off processes. Need a generic pipeline so any connector can automatically trigger the full mining chain.

## Decision

**7-Stage Pipeline (built into BaseConnector):**

```
Stage 1: Validate      — connector.validate(entity_type, record)
Stage 2: Normalize     — connector.normalize(entity_type, record)
Stage 3: Persist       — connector.persist(entity_type, record, cursor)
Stage 4: Mine          — connector.post_persist(entity_type, result) → n8n webhook
Stage 5: Knowledge Graph — n8n workflow updates project_brain, vendor graph, lessons
Stage 6: Executive     — mining results surface to executive_inbox if insight threshold met
Stage 7: Sync State    — connector_sync_state.last_synced_at updated
```

**n8n Integration (Stage 4):**
- Connector's `post_persist()` fires `N8N_HOUZZ_SYNC_WEBHOOK` with `{event, entity_type, inserted, updated}`
- n8n workflow routes by entity type to appropriate miner
- Miner output → knowledge graph → executive aggregator → inbox

**Incremental by default:**
- `connector_sync_state.last_synced_at` is the watermark
- Browser Agent queries this before extraction: only extract records changed since watermark
- Connector updates watermark after successful persist

**Autonomous Recovery (Stages 1-4):**
- Max 3 retries per entity type batch
- Exponential backoff: 2s, 5s, 15s
- After 3 failures: log to `notification_log` with severity=CRITICAL → executive_inbox escalation
- `connector_sync_state.status` set to 'error', `retry_count` incremented

## Consequences

**Positive:**
- Any new connector automatically gets retry, sync state, event publishing, and executive reporting
- Mining chain triggered automatically — no manual API calls
- Failure visibility: `connector_sync_state` shows every entity type's status

**Negative:**
- n8n webhook must be configured (`N8N_HOUZZ_SYNC_WEBHOOK` env var) to trigger Stage 4+
- Knowledge graph update logic must be implemented in n8n workflows (Sprint 5)
