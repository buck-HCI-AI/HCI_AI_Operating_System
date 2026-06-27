# ADR-002: Browser Agent as Discovery-Only Agent

**Status:** Accepted | **Date:** 2026-06-27 | **Author:** Claude Code (Autonomous Development Mode)

## Context

Browser Claude (the browser-automation Claude instance) was being used ad-hoc — sometimes producing structured data, sometimes writing notes to files. It had no standard protocol for what to extract, what format to produce, or where to deliver it.

## Decision

**Immutable division of labor:**

| Role | Agent | Allowed Actions |
|------|-------|-----------------|
| Discovery | Browser Claude | Navigate, extract, produce canonical JSON, call /ingest API |
| Validation | Claude Code Connector | Validate schema, required fields, business rules |
| Normalization | Claude Code Connector | Canonical field names, date formats, money types |
| Persistence | Claude Code Connector | Upsert to DB via connector, never direct SQL |
| Mining | Claude Code Miners | Trigger from connector post-persist hook |
| Analysis | Claude Code AI | Analyze mined data, produce executive intelligence |

**Browser Claude NEVER:**
- Writes directly to the database
- Executes SQL
- Runs migrations
- Makes approval decisions

**Browser Claude ALWAYS:**
- Includes `dry_run: true` in initial extraction (Claude Code validates before flipping)
- Includes `extracted_at` timestamp (ISO 8601 UTC)
- Includes `raw_data` field with original platform fields for audit trail
- Generates stable, reproducible IDs for records without native IDs

## Protocol

See `BROWSER_AGENT_STANDARD.md` for complete canonical JSON schemas and step-by-step extraction protocol.

## Consequences

**Positive:**
- Browser Agent can be replaced (Selenium, Playwright, manual extraction) without changing DB schema
- All validation logic in one place (connector) — no schema drift
- Dry-run by default prevents accidental writes from Browser Agent errors
- Audit trail: `raw_data` + `synced_at` in every table

**Negative:**
- Browser Agent must follow the canonical format — freeform extraction won't work
- Two-step process for first-time extraction (dry_run → review → write)
