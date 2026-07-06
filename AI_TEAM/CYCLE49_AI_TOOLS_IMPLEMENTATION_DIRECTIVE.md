# CYCLE49 — AI Tools & Integration Implementation Directive

> **SPRINT LABEL SUPERSEDED 2026-07-06 (Claude Code, drift-check finding):** the "Sprint 9"
> reference below is Browser Claude's own independent numbering, never reconciled against
> `CURRENT_SPRINT.md` (canonical: Sprint 3, active since 2026-07-01). The two proposed
> integrations below (Perplexity research, Weather API) were never built — confirmed via
> `grep` against `gbt_gateway.py`, no `/gateway/research` or `/gateway/project/{code}/weather`
> routes exist. Both still require Buck to supply API keys before implementation can start;
> flagged to him 2026-07-06 as a still-open decision, not silently actioned.

**Date:** 2026-07-02 | **Author:** Browser Claude | **Source:** RECOMMENDED_TOOLS_SPEC.md | **Priority:** P0

## P0 — Sprint 9 (Implement Now)

### 1. Perplexity AI — Research Intelligence
API: pplx-api.perplexity.ai | Model: sonar-pro | API key: Buck to provide
Endpoint: POST /gateway/research {query, project_code?, context?}
Response: {answer, citations, confidence, stored_in_brain}
Use cases: material pricing, local code research, sub reputation, HVAC lead times
Integration: store in project brain if project_code provided

### 2. Weather API — Environmental Intelligence
API: OpenWeatherMap (free tier) | 1 call/day/project keyed to site coordinates
Endpoint: GET /gateway/project/{code}/weather
Response: {current, forecast_7d, alerts, schedule_risk: bool}
Cron: 05:00 MT daily. Severe forecast -> production_risk + Telegram alert to Buck
LOW complexity. Implement first.

## P1 — Sprint 9-10

### 3. AI Plan Reader Phase 1 — PDF Text Extraction
Library: PyMuPDF (fitz) or pdfplumber
Endpoint: POST /gateway/plan/parse {project_code, file_url or file_content}
Response: {keynotes, spec_refs, schedules, equipment_list, room_list, extraction_confidence}
Store results in project brain as plan_extraction record

### 4. CPM Scheduling Engine
New tables:
- schedule_activities (id, project_id, name, duration_days, planned/actual start/end, ES/EF/LS/LF, total_float, is_critical)
- schedule_relationships (id, predecessor_id, successor_id, relationship_type FS/SS/FF/SF, lag_days)
- schedule_baselines (id, project_id, baseline_date, activities_json)
Algorithm: Forward pass ES/EF -> Backward pass LS/LF -> Float=LS-ES -> Critical=Float==0
Endpoints: GET /gateway/project/{code}/schedule/critical-path, /float, POST activity, PUT activity/{id}/complete

### 5. Cost Forecasting Engine (EVM)
New tables:
- project_budgets (id, project_id, trade, csi_division, budget_amount, committed, actual, earned_value_pct)
- cost_forecasts (id, project_id, forecast_date, projected_final, projected_variance, projected_variance_pct, confidence, trade_breakdown)
Endpoints: GET /gateway/project/{code}/cost-forecast, /budget, POST /budget/line
Cron: Weekly Monday 06:00 MT. Alert if any trade > 5% variance.

## P2 — Sprint 10+

### 6. Photo AI
Models: Claude Vision or GPT-4V (existing API keys)
POST /gateway/project/{code}/photo/analyze {image_url, notes}
Response: {observations, safety_flags, progress_tags, stored_event_id}

### 7. Subcontractor Portal
FastAPI + plain HTML. Unique token per vendor/project.
GET /portal/{token}, POST /portal/{token}/bid, /lien-waiver, /po-acknowledge

### 8. QuickBooks
CYCLE32 spec complete. BLOCKED on Buck: developer.intuit.com -> Client ID + Secret -> send to Code via Telegram.

## Implementation Order
1. Weather API (lowest complexity)
2. Perplexity AI
3. Plan Reader Phase 1
4. CPM Engine + Cost Forecast (design DDL together)
5. Photo AI
6. Sub Portal
7. QuickBooks (after Buck unblocks)

## Rules
- All endpoints: X-API-Key auth, standard gateway response envelope
- Test data: project_id=28 (QATEST) only
- Confirm each tool live via POST /gateway/ai/messages to browser_claude
