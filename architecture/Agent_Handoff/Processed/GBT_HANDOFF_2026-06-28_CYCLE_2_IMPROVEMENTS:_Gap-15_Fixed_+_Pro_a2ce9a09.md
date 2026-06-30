---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: CYCLE 2 IMPROVEMENTS: Gap-15 Fixed + Procurement Risk Built + System Cleaned
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

# Claude Code: Cycle 2 Improvements — 2026-06-28

## WHAT CHANGED

### 1. GAP-15 FIXED: Health Score Now Includes Bid Coverage

Previously: 64EW showed GREEN despite 94% of packages having zero bids.
Now: Health scoring includes procurement as a first-class signal.

Live project status (real, as of now):
- 64EW: RED — only 6% bid coverage (2/35 packages have bids)
- 101F: RED — only 4% bid coverage (1/26 packages)
- 1355R: YELLOW — 38% bid coverage (23/61 packages)
- 246GW: RED — 0% bid coverage (0/44 packages)

Health logic: <25% coverage + 5+ packages = RED. 25-49% = YELLOW. This is the real state of procurement on these jobs.

### 2. NEW ENDPOINT: Procurement Risk View

GET /gateway/project/{code}/procurement-risk

Buckets every package into: no_bids / single_bid / competitive / awarded.
Returns: risk_score (red/yellow/green), bid_coverage_pct, spread analysis.
MCP tool: GetProcurementRisk(project_code)

1355R result: RED | 38% coverage | 38 packages with no bids, 23 single-bid, 0 competitive

### 3. 1355R PENDING BIDS IMPORTED

3 bids that were in email/Drive but not in DB — now imported:
- Two Rivers Design Center (Div 11A Appliances) — received June 23
- Ellis Design Inc (Div 11A Appliances) — pending appliance PDF
- Kubed Fire (Div 13A Fire Suppression) — received June 22
HubSpot deal IDs linked: 321397739194 (appliances), 321363190466 (fire suppression)

### 4. ASPN SCENARIO PROJECTS MOVED TO REFERENCE

ASPN-NEW, ASPN-REM, ASPN-MC were showing in executive reports as live projects with RED health.
Moved to status=reference. They now supply: lessons, historical cost records, Qdrant vectors.
Project registry is clean: exactly 4 live ops projects.

### 5. _get_pid IS DB-DRIVEN + project_code COLUMN ADDED

All 20 real projects now have a project_code column in DB.
Lookup is a DB query — no more hardcoded dict. New projects auto-register.

## SYSTEM STATE NOW

- Gateway: 34 services | 55 MCP tools
- Projects: 4 live ops | 16 reference | 0 test
- Vendors: 294 | Lessons: 37 | Cost records: 60 | Bid entries: 325

## WHAT GBT SHOULD DO NEXT

1. Run GetProcurementRisk on 64EW, 101F, 1355R, 246GW to see the real bid gaps
2. Run GetMarketRates for Div 15 (HVAC) and Div 06 (carpentry) to see 2026 Aspen pricing
3. Run GetROMEstimate(sf=4000, project_type=new) to test the ROM calibration
4. Confirm: should 83SB (Sagebrusch) be investigated? It has no team, no data, status=reference.

*Claude Code — Learn → Build → Test → Report cycle 2 complete.*
