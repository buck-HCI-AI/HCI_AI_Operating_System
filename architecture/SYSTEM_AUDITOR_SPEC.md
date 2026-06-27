# Autonomous System Auditor — Specification
*Phase 3, BTW-1 | Active | Updated: 2026-06-27*

## Purpose

Nightly self-evaluation of the entire HCI AI platform. Detects issues,
scores system health, generates actionable recommendations, and
(where safe) applies auto-fixes.

## Service Location

`services/system_auditor/` — mounted at `/api/v1/services/system-auditor`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/run` | Trigger full audit (5-15 seconds) |
| GET | `/latest` | Most recent stored report |
| GET | `/history?days=30` | Health score trend over time |
| GET | `/recommendations` | Actionable improvement list |

## Audit Domains (8 sections)

| Domain | What It Checks | Weight |
|--------|---------------|--------|
| API Health | 18 service endpoints — latency, uptime | 30% |
| Connector Health | Sync staleness, errored connectors, missing integrations | 10% |
| Workflow Health | n8n active/inactive workflows, disk vs n8n diff | 10% |
| Test Coverage | Services with/without test files, pass rates | 15% |
| Documentation Coverage | 9 required spec docs, service READMEs | 10% |
| Technical Debt | TODO/FIXME/HACK counts, placeholder services | 10% |
| Data Freshness | Key table staleness, Houzz data availability | 10% |
| Security Review | .env tracking, hardcoded credentials, auth middleware | 15% |

## Health Score

Overall score 0-100 (weighted average of domain scores):
- 80-100: HEALTHY
- 60-79: NEEDS_ATTENTION
- 40-59: DEGRADED
- 0-39: CRITICAL

## Persistence

Table: `system_audit_reports` — UNIQUE on `audit_date`
ON CONFLICT: updates all domain scores for idempotent re-runs.

## Auto-Fix Policy

Only apply auto-fixes that are:
- Local file system changes (no network writes)
- Reversible (no data deletion)
- Non-production (no external API calls)

Human approval required for: DB schema changes, n8n workflow activation,
external API writes, production configuration changes.

## Recommendation Format

```json
{
  "priority": "HIGH",
  "category": "connectors",
  "title": "2 connectors stale >7 days",
  "action": "Review sync schedules and credentials",
  "auto_fixable": false,
  "requires_human": false
}
```
