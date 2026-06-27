# ADR-001: Universal Connector Framework

**Status:** Accepted | **Date:** 2026-06-27 | **Author:** Claude Code (Autonomous Development Mode)

## Context

HCI AI OS must integrate with 7+ SaaS platforms (Houzz, HubSpot, Outlook, QuickBooks, Google Drive, Procore, Autodesk). Without a standard, each integration becomes one-off code with different validation, persistence, error handling, and sync tracking patterns. The Browser Agent was extracting data but had no standard for what to produce or where to send it.

## Decision

Implement a Universal Connector Framework with:

1. **`BaseConnector`** — abstract base class in `services/connectors/base_connector.py`
   - 7-stage pipeline: Discover → Validate → Normalize → Persist → Mine → Knowledge Graph → Executive Reporting
   - Autonomous recovery: 3 retries with exponential backoff (2s, 5s, 15s)
   - `connector_sync_state` table tracks last sync per entity per project
   - Dry-run default: all connectors default to `dry_run=True`

2. **`HouzzConnector`** — reference implementation in `services/connectors/houzz_connector.py`
   - All 17 entity types with typed upsert handlers
   - Post-persist hook triggers n8n webhook for downstream miners

3. **Connector Routes** — `services/connectors/routes.py`
   - `GET /api/v1/services/connectors` — list all registered connectors
   - `POST /api/v1/services/connectors/{name}/ingest` — Browser Agent entry point

4. **Browser Agent Standard** — `BROWSER_AGENT_STANDARD.md`
   - Division of labor: Browser = Discovery, Claude Code = Validate/Persist
   - Canonical JSON schemas for all 17 Houzz entity types
   - Incremental sync protocol (changed_since / last_synced_at)

## Consequences

**Positive:**
- New platform integrations = implement `validate()`, `normalize()`, `persist()` — framework handles the rest
- Incremental sync built in — only changed records extracted and sent
- Autonomous recovery — transient failures retried without Buck involvement
- All sync activity auditable via `connector_sync_state` table
- Dry-run default prevents accidental writes

**Negative:**
- Browser Agent must produce canonical JSON (learning curve for first extraction)
- Cannot extract real-time data without Browser Agent being online

## Schema Changes

Migration 009 adds:
- `connector_sync_state` — universal sync tracker
- `houzz_files`, `houzz_time_entries`, `houzz_tasks`, `houzz_messages`
- `houzz_budget`, `houzz_estimates`, `houzz_contracts`, `houzz_purchase_orders`
- `houzz_change_orders`, `houzz_selections`, `houzz_project_vendors`
- `houzz_contacts`, `houzz_team_members`, `houzz_subcontractors`
