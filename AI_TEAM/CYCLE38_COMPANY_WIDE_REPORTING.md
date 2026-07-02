# CYCLE 38 — Company-Wide Portfolio Reporting
**GBT Cycle:** 38
**Sprint:** 8
**Priority:** P1 — Company-Wide Visibility
**Status:** SPEC — Pending Code Implementation
**Date:** 2026-07-02
**Author:** Browser Claude (BC)

---

## Problem Statement

HCI Project Status GPT currently has no endpoint to retrieve all active projects in a single call. Superintendents and Buck need a company-wide portfolio view — all 4 active jobs, aggregated risks, open decisions, and procurement delays — in one response, not 4 separate queries.

Mission Control snapshot shows: 3 of 4 projects at risk (101F RED, 1355R RED, 64EW YELLOW). A portfolio summary endpoint enables management-level briefings without querying each project individually.

---

## Architecture Decision

**ADR-S8-004: Portfolio Aggregation at Gateway Layer**
- Portfolio endpoints aggregate across all active projects server-side
- No client-side aggregation — single call returns complete picture
- Consistent with: "Treat the database as the system of record"
- Field-First Design (ADR-S8-003): portfolio view must be readable on mobile

---

## Endpoints Required

### 1. GET /gateway/portfolio/summary
Returns all active projects with top-line status in one call.

**Response shape:**
```json
{
  "generated_at": "2026-07-02T12:00:00MT",
    "company_health": "RED",
      "active_project_count": 4,
        "projects": [
            {
                  "code": "101F",
                        "name": "101 Francis",
                              "status": "RED",
                                    "top_risk": "Steel supplier 5 days behind GATE2-TS02b",
                                          "severity": "critical",
                                                "open_risks": 3,
                                                      "open_decisions": 2,
                                                            "schedule_variance_days": 5
                                                                }
                                                                  ],
                                                                    "company_totals": {
                                                                        "open_risks": 12,
                                                                            "critical_risks": 3,
                                                                                "open_decisions": 8,
                                                                                    "procurement_delays": 4
                                                                                      }
                                                                                      }
                                                                                      ```

                                                                                      ### 2. GET /gateway/portfolio/risks
                                                                                      All open risks across all projects, sorted by severity.

                                                                                      **Query params:** `?severity=critical|high|medium|low` (optional filter)

                                                                                      ### 3. GET /gateway/portfolio/decisions
                                                                                      All open decisions across all projects requiring action.

                                                                                      **Query params:** `?owner=buck` (optional filter by decision owner)

                                                                                      ### 4. GET /gateway/portfolio/procurement
                                                                                      All procurement delays and long-lead material alerts across all jobs.

                                                                                      ---

                                                                                      ## Implementation Notes for Code

                                                                                      - Source data: existing `project_risks`, `decisions`, `procurement_items` tables
                                                                                      - Auth: X-API-Key header required (write endpoints) — reads can be open per gateway pattern
                                                                                      - Cache: Redis cache 5-minute TTL on /portfolio/summary (high-read endpoint)
                                                                                      - Company health roll-up logic:
                                                                                        - RED if any project is RED
                                                                                          - YELLOW if any project is YELLOW and none RED
                                                                                            - GREEN if all projects GREEN
                                                                                            - Active projects defined as: status = 'active' in projects table
                                                                                            - Test sandbox (project_id=28 QATEST) excluded from portfolio aggregation

                                                                                            ---

                                                                                            ## GPT Integration

                                                                                            Once endpoints are live, add to HCI Project Status GPT Actions schema:
                                                                                            - `getPortfolioSummary` → GET /gateway/portfolio/summary
                                                                                            - `getPortfolioRisks` → GET /gateway/portfolio/risks
                                                                                            - `getPortfolioDecisions` → GET /gateway/portfolio/decisions
                                                                                            - `getPortfolioProcurement` → GET /gateway/portfolio/procurement

                                                                                            Trigger phrase for GPT: "give me all project update" or "company status" or "portfolio"

                                                                                            ---

                                                                                            ## Success Criteria

                                                                                            - [ ] GET /gateway/portfolio/summary returns all 4 active projects in one call
                                                                                            - [ ] Company health roll-up (RED/YELLOW/GREEN) calculated correctly
                                                                                            - [ ] HCI Project Status GPT calls portfolio endpoint on "give me all project update"
                                                                                            - [ ] Response readable on mobile viewport (469px)
                                                                                            - [ ] QATEST project_id=28 excluded from results
                                                                                            - [ ] Redis cache confirmed working (second call faster than first)
                                                                                            - [ ] 109/109 existing tests still passing after implementation

                                                                                            ---

                                                                                            ## Directive Reference

                                                                                            - Gateway directive posted: request_id e9acdd3e
                                                                                            - Related: CYCLE37_SPRINT8_PREVIEW.md
                                                                                            - ADR: ADR-S8-003 (Field-First), ADR-S8-004 (Portfolio Aggregation)
                                                                                            - Code channel: Post implementation report to ai_messages when complete

                                                                                            ---

                                                                                            *Generated by Browser Claude — 2026-07-02 — Per never-stop directive*
