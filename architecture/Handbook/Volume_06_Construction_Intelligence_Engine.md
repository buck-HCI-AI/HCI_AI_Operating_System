# Volume VII — Construction Intelligence Engine
*HCI AI Construction Operating System Architecture Handbook*

---

## 7.1 Engine Overview

The Construction Intelligence Engine is the collection of specialized services that analyze
project data and produce domain-specific insights. Each service extends `BaseIntelligenceService`.

---

## 7.2 Intelligence Services — Current State (✅ Implemented)

### Service Map

```
services/
├── base.py                       ← BaseIntelligenceService (all services inherit)
├── project_brain/                ← Per-project health, risks, AI summary
├── cross_project/                ← Portfolio comparison, company snapshot
├── predictive_engine/            ← 7 forward-looking predictions + confidence
├── system_auditor/               ← 8-domain nightly self-evaluation
├── bid_intelligence/             ← Bid analysis per project
├── bid_leveling/                 ← Bid comparison + gap detection
├── vendor_intelligence/          ← Vendor performance analytics
├── procurement/                  ← Procurement workflow intelligence
├── schedule_intelligence/        ← Schedule risk analysis
├── risk_intelligence/            ← Risk tracking + escalation
├── document_intelligence/        ← Document discovery + extraction
├── decision_intelligence/        ← Decision pattern recognition
├── kpi_intelligence/             ← KPI snapshot + trending
├── historical_cost/              ← Cost overrun patterns, benchmarking
├── lessons_learned/              ← Lesson capture + retrieval
├── approval_queue/               ← Approval workflow management
├── notification_engine/          ← ntfy + email + push delivery
├── autonomy/                     ← Automation opportunity detection
├── background_learning/          ← Background document processing
├── connectors/                   ← Integration health monitoring
├── connector_registry/           ← Integration catalog
├── houzz_intelligence/           ← Houzz-specific data processing
├── operating_rules/              ← SOP rule engine
├── business_process_library/     ← Process template library
└── sop_execution/                ← SOP workflow execution
```

### BaseIntelligenceService Interface (✅)

```python
class BaseIntelligenceService:
    # PostgreSQL access
    pg_query(sql, params) → list[dict]
    pg_one(sql, params)   → dict
    pg_execute(sql, params)

    # Cache (Redis)
    cache_get(key)
    cache_set(key, value, ttl)

    # Vector search (Qdrant)
    search(query, collection, limit, project_filter) → list

    # AI synthesis (Haiku)
    ask_claude(prompt, system, max_tokens) → str
    parse_json_response(raw) → dict
```

---

## 7.3 Risk Engine (✅ Implemented — to be expanded)

### Current Detectors
- Procurement risks: `_procurement_risks()` in `intelligence.py`
- Schedule risks: `_schedule_risks()` — from `schedule_variance` table
- Decision risks: `_decision_risks()` — from `executive_inbox`
- Budget risks: `_budget_risks()` — from `houzz_budget` + `historical_cost_records`
- Data gap risks: `_data_gap_risks()` — from `_data_completeness()`

### Risk Record Schema
```sql
TABLE project_risks_computed (
    project_id     INTEGER,
    risk_code      TEXT,    -- PROC-001, SCHED-002, etc.
    risk_type      TEXT,    -- procurement | schedule | budget | decision | data
    severity       TEXT,    -- critical | high | medium | low
    title          TEXT,
    description    TEXT,
    evidence       TEXT,
    confidence     NUMERIC,
    mitigation     TEXT,
    status         TEXT,    -- open | resolved
    detected_at    TIMESTAMPTZ,
    resolved_at    TIMESTAMPTZ
)
```

---

## 7.4 Sections Requiring Chief Architect Input (⚠️)

### 7.4.1 Risk Engine Design Philosophy
*[Chief Architect: How should the risk engine prioritize and weight different risk signals?
What risk patterns are unique to Hendrickson Construction?]*

### 7.4.2 Schedule Intelligence Model
*[Chief Architect: How should the system reason about construction schedule interdependencies?]*

### 7.4.3 Cost Intelligence Model
*[Chief Architect: How should historical cost data inform current project predictions?
What variance thresholds are acceptable vs alarming for HCI?]*

### 7.4.4 Vendor Intelligence Model
*[Chief Architect: How should the system evaluate vendor performance, capacity, and reliability?]*

### 7.4.5 Labor Intelligence
*[Chief Architect: Define what labor intelligence the system should track and predict]*

### 7.4.6 Client Intelligence
*[Chief Architect: Define how the system should track and surface client relationship signals]*

### 7.4.7 Prediction Model Confidence Thresholds
*[Chief Architect: At what confidence level should a prediction trigger an alert vs be surfaced passively?]*

---

*Ref: [architecture/CONSTRUCTION_INTELLIGENCE_MODEL.md](../architecture/CONSTRUCTION_INTELLIGENCE_MODEL.md)*
