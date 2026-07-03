# Volume VI — Construction Intelligence Engine
*HCI AI Construction Operating System Architecture Handbook*

---

## 6.1 Engine Overview + Intelligence Engine Philosophy
*Philosophy authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

The Construction Intelligence Engine is the collection of specialized services that analyze
project data and produce domain-specific insights. Each service extends `BaseIntelligenceService`.

### Why the Intelligence Is Modular

The HCI AI OS intelligence layer is composed of twenty-plus specialized services rather than a single monolithic intelligence engine. This is deliberate and deliberately unusual — most AI implementations choose the monolith: one large model that handles everything. HCI chose modularity.

**Reason 1: Construction intelligence is domain-specific at the sub-task level.** Bid leveling analysis requires knowledge of trade categories, CSI divisions, and outlier pricing detection. Schedule analysis requires dependency relationships and critical path methodology. Risk detection requires encoding of construction-specific risk patterns. These are genuinely different domains of expertise — modularity lets each be implemented by a service that specializes in it, with its own detection logic, confidence calibration, and evidence format.

**Reason 2: Modularity enables independent improvement.** When the bid leveling service gets more accurate, only that service needs to change. The schedule and risk services are unaffected. Changes are isolated, testable, and deployable independently — a monolithic model that improves in one area changes everything else too, and you cannot verify the improvement without re-testing the whole system.

**Reason 3: The BaseIntelligenceService pattern enforces auditability.** Every service that inherits from it produces output in the same format: data + confidence + evidence + metadata. Any consumer of intelligence — the Project Brain, the role consoles, the workflow engine — can evaluate any intelligence output the same way, regardless of which service produced it. Auditability is not optional in a governance-constrained environment; the modular pattern makes traceability structural, not an afterthought.

**The Anti-Pattern We Rejected:** A single "project intelligence" endpoint returning a comprehensive assessment from a large language model is superficially simpler but less auditable (LLM reasoning is opaque), less reliable (outputs vary between runs on identical inputs), less correctable (you cannot tune one aspect without affecting others), and more expensive. The modular service architecture makes the system's intelligence inspectable, correctable, and improvable at the level that matters — the right trade-off for HCI's context.

---

## 6.2 Intelligence Services — Current State (✅ Implemented)

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

## 6.3 Risk Engine (✅ Implemented — to be expanded)

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

## 6.4 Sections Requiring Chief Architect Input (⚠️)

### 6.4.1 Risk Detection Architecture
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

**The Canonical Risk Detection Pattern**

All risk detection services in the HCI AI OS follow the same pattern, so future services can be added consistently.

Every risk detection method follows the signature `_detect_{category}_risks(project_id, project_data) → List[RiskRecord]`, where category is one of procurement, schedule, budget, decision, data_gap (or a new category added via ACR).

Every detected risk produces a RiskRecord with: project_id, category, severity (critical/high/medium/low), title (max 120 chars, action-oriented — e.g. "No bids for Mechanical HVAC — deadline in 3 days"), description, evidence (a list of `{field, value, threshold, significance}` items), confidence (0.0–1.0), recommended_action, detected_at, and status.

**The Non-Duplication Check:** Before inserting a new RiskRecord, the system queries for an existing record with the same project, category, and matching title in an open/acknowledged/in-response status. If found, it updates last_detected_at and re-evaluates severity rather than inserting a duplicate.

**The Evidence Format:** Evidence items must be specific and quantitative. `{field: "bid_coverage_pct", value: 6, threshold: 30, significance: "Only 2 of 35 packages have bids received"}` is defensible; `{field: "procurement", value: "low", significance: "Not many bids"}` is not. Vague evidence gets a risk dismissed or ignored; specific evidence compels action.

**Adding a New Risk Category (requires ACR):** define the category's scope, implement `_detect_{category}_risks()` following the canonical pattern, register it in the RiskDetectionService orchestrator, define its evidence format, set initial confidence calibration, write unit tests against known data, and run in shadow mode (detect but don't surface) for two weeks before activating. New categories must not overlap existing ones — overlap creates duplicate risk records that clutter the approval queue.

### 6.4.2 Schedule Intelligence Model
*Authored by: Chief Architect (ChatGPT) — 2026-07-02*

Schedule intelligence extends beyond tracking dates. The HCI AI Operating System evaluates the dependency relationships that determine whether a project can successfully advance through construction.

The model continuously analyzes predecessor and successor activities, procurement lead times, inspections, permitting requirements, owner decisions, design dependencies, subcontractor sequencing, and long-lead material availability. Individual activities are evaluated according to their impact on downstream work rather than their duration alone.

Critical-path activities receive the highest level of continuous monitoring because small delays may propagate throughout the project. Non-critical activities are evaluated according to available float, downstream dependencies, and opportunities for recovery before becoming operational concerns.

The objective is early awareness rather than retrospective reporting. Schedule intelligence should identify developing constraints while corrective action remains practical, allowing project teams to mitigate impacts before schedule variance becomes project delay.

### 6.4.3 Cost Intelligence Model
*Authored by: Chief Architect (ChatGPT) — 2026-07-02*

Cost intelligence combines historical project performance with current project conditions to provide context for financial decision-making rather than replacing formal estimating or accounting processes.

Historical costs establish expected performance ranges for comparable scopes of work. Current bids, procurement activity, schedule conditions, market factors, and project-specific constraints are evaluated against these historical baselines to identify meaningful variance requiring management attention.

Not every variance represents risk. Minor deviations that remain within established historical experience should be surfaced as informational context rather than operational alerts. Significant departures from expected performance, rapidly changing trends, repeated overruns within a trade, or accumulating variance across multiple work packages warrant progressively higher visibility and earlier management review.

The purpose of cost intelligence is to identify developing financial conditions while meaningful corrective action remains available. Historical knowledge provides context; current project conditions determine operational significance.

### 6.4.4 Vendor Intelligence Model
*Authored by: Chief Architect (ChatGPT) — 2026-07-02*

Vendor intelligence evaluates trade partners through demonstrated operational performance rather than isolated project outcomes. Every completed project contributes measurable evidence that improves future procurement decisions.

The model considers schedule reliability, responsiveness, bid completeness, quality performance, communication consistency, change-order behavior, issue resolution, historical participation, workload indicators, and demonstrated ability to perform comparable scopes of work. No single project defines vendor capability; long-term performance establishes organizational confidence.

Vendor intelligence also evaluates operational capacity. A highly capable vendor with insufficient available capacity may present greater project risk than a qualified vendor able to fully support the required schedule. Procurement recommendations therefore balance demonstrated performance with current workload and project timing.

The objective is informed procurement rather than automated vendor selection. AI identifies relevant history, highlights patterns, and presents supporting evidence. Project teams continue to evaluate commercial considerations, relationships, negotiations, and project-specific requirements before making award decisions.

### 6.4.5 Labor Intelligence
*Authored by: Chief Architect (ChatGPT) — 2026-07-02*

Labor intelligence provides operational awareness of workforce availability, productivity, and resource demand across active projects. Its purpose is to identify emerging staffing constraints before they affect project execution.

The model evaluates planned versus actual staffing levels, trade sequencing, forecast labor demand, schedule-driven workforce requirements, seasonal influences, known resource constraints, and historical production performance. Labor availability is considered alongside procurement, schedule, and subcontractor readiness because construction performance depends upon the coordinated availability of all three.

Historical project data continuously improves workforce planning by identifying typical staffing patterns for comparable project types, recognizing recurring bottlenecks, and highlighting periods where labor shortages have historically affected project delivery.

Labor intelligence supports planning rather than directing personnel assignments. Final staffing decisions remain the responsibility of project leadership, who balance operational priorities, individual capabilities, safety, subcontractor commitments, and changing field conditions. The platform provides visibility into developing workforce needs so decisions can be made earlier, with better information, and with fewer operational surprises.

### 6.4.6 Client Intelligence
*[Chief Architect: Define how the system should track and surface client relationship signals]*

### 6.4.7 Prediction Model Confidence Thresholds
*[Chief Architect: At what confidence level should a prediction trigger an alert vs be surfaced passively?]*

---

*Ref: [architecture/CONSTRUCTION_INTELLIGENCE_MODEL.md](../architecture/CONSTRUCTION_INTELLIGENCE_MODEL.md)*
