# ADR-005: Autonomous Nightly System Auditor

**Date**: 2026-06-19
**Status**: Accepted
**Author**: Claude Code
**Reviewers**: Buck Adams

---

## Context

Phase 3 required a system that could monitor its own health and alert on degradation
without requiring Buck to manually run checks. The auditor needed to be autonomous
but not destructive.

## Decision

**SystemAuditor** runs nightly at 02:00 via n8n, probing 8 audit domains and producing
a health score (0-100) with recommendations. Auto-fix applies only to low-risk issues;
all other findings are reported, not acted on.

**Weighted scoring model:**

| Domain | Weight | Rationale |
|---|---|---|
| API Health | 30% | Platform useless if endpoints are down |
| Security | 15% | Credential exposure is catastrophic |
| Test Coverage | 15% | Tests are quality gate |
| Connector Health | 10% | Data freshness depends on connectors |
| Workflow Health | 10% | Automation value |
| Documentation | 10% | Maintainability |
| Tech Debt | 10% | Long-term quality |
| Data Freshness | 10% | Intelligence quality |

**Health labels:**
- 90–100: EXCELLENT
- 75–89: HEALTHY
- 60–74: NEEDS ATTENTION
- <60: CRITICAL

## Rationale

API health gets the highest weight because an API with poor health makes all other
scores irrelevant — no dashboards, no intelligence, no automation works. Security comes
second because a credential leak is unrecoverable by any other mechanism.

The auto-fix constraint (low-risk only) preserves the constitutional principle that
AI cannot take destructive actions without human approval. "Low-risk" is defined as:
adding indexes, updating stale metadata, clearing expired cache — never deleting,
never modifying application logic.

## Consequences

**Positive**:
- Nightly push notification to Buck's phone about system health
- Self-improvement loop: system tells you what it needs
- Audit history enables trend analysis

**Negative**:
- 02:00 cron may miss degradation that happens and recovers before midnight
- 8-domain score can mask a failing domain that's low-weight

## Implementation

- `services/system_auditor/routes.py` — `SystemAuditor` class
- `05_Database/migrations/014_system_auditor.sql` — `system_audit_reports` table
- `03_Source_Code/workflows/n8n/AUTO-NIGHTLY-AUDIT.json` — activated workflow (ID: XIihPRTFx27A18Vy)
- Audit results persisted via UPSERT ON CONFLICT audit_date (one row per day)
