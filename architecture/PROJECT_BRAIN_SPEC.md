# Project Brain — Specification
*Phase 2, Sprint 4 | Active | Updated: 2026-06-27*

## Purpose

Per-project persistent intelligence layer. Aggregates all available data,
detects risks automatically, scores project health (RED/YELLOW/GREEN),
and generates AI-powered narrative summaries.

## Service Location

`services/project_brain/` — mounted at `/api/v1/services/project-brain`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/{id}/intelligence` | Full snapshot with all data sources |
| GET | `/{id}/health` | RED/YELLOW/GREEN + risk counts |
| GET | `/{id}/risks` | All detected risks with evidence |
| GET | `/{id}/summary` | AI narrative + recommended actions |
| GET | `/{id}/health-history` | Trending health over last N days |

## Risk Detection

```python
_procurement_risks()  # PROC-001, PROC-002, PROC-003
_schedule_risks()     # SCHED-001, SCHED-002, SCHED-003
_decision_risks()     # DEC-001 (decisions >3 days old)
_budget_risks()       # BUDGET-001, BUDGET-002
_data_gap_risks()     # DATA-001 (completeness <60%)
```

## Data Persistence

Table: `project_brain_snapshots` — upserted daily per project
- `UNIQUE(project_id, snapshot_date)`
- Stores: health, health_factors, risk_count, budget_exposure,
  schedule_variance_days, open_decisions, open_bids, ai_summary, data_completeness_pct

Table: `project_risks_computed` — individual risk records per project

## AI Summary

Uses `BaseIntelligenceService.ask_claude()` with Haiku for fast synthesis.
Generates: 3-sentence narrative + 3 recommended actions.
Triggered when `include_ai_summary=True` (default).
