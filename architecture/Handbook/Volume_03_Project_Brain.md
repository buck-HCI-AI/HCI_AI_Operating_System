# Volume III — Project Brain
*HCI AI Construction Operating System Architecture Handbook*

---

## 3.1 What Is the Project Brain?
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### Definition

The Project Brain is a persistent, intelligent memory system that accumulates, organizes, and reasons over all information related to a specific construction project throughout its lifecycle.

It is not a database. Databases store records. The Project Brain stores records AND contextualizes them, connects them, reasons over them, and returns synthesized intelligence that a database cannot return.

It is not a document repository. Document repositories hold files. The Project Brain reads the documents, extracts the intelligence within them, maps relationships between them, and makes that intelligence available for reasoning.

It is not a project management tool. Project management tools provide workflows and tracking. The Project Brain provides memory — a complete and queryable record of everything that has happened on the project, what was decided, by whom, on what evidence, with what outcome.

**The operational definition:** The Project Brain is what a highly experienced senior PM would know about a project if they had read every document, attended every meeting, reviewed every bid, and tracked every risk since day one — and could recall any of it instantly, in any context.

### How It Learns

The Brain accumulates knowledge through five mechanisms:

**1. Event Logging** — Every significant event is logged to the project event history. The event log is immutable — events can be added but not modified or deleted. Over the life of a project, the event log becomes a complete operational history.

**2. Document Indexing** — When a new document is added to the project Drive folder, the Background Learning connector detects it, reads it, extracts key information (specs, open items, decisions, deadlines), and stores the extracted intelligence in the Brain. The document itself stays in Drive — the Brain stores what matters about it.

**3. Conversation Memory** — Every AI interaction with the project is stored. When the PM asks a status question, the question and answer are logged. When the same question is asked days later, the Brain can show trend context without requiring the PM to remember where it was before.

**4. Risk Evolution** — When a risk is detected, updated, resolved, or closed, each state change is logged. The risk history shows how it evolved and becomes training data for improving future detection.

**5. Decision Recording** — When Buck or a PM makes a decision, that decision is logged to the Brain with the date, the decision maker, the alternatives considered, and the rationale. Over time, this decision record helps the system understand HCI's decision-making patterns.

### What It Accumulates Over a Project Lifecycle

Phase 1 (Pre-Construction, bidding): bid packages, received bids, procurement risks, vendor recommendations, budget-vs-estimate tracking.

Phase 2 (Pre-Construction, permits and submittals): permit applications, submittal log, RFI register, design decision record, schedule baseline.

Phase 3 (Construction): daily field notes, daily reports, inspection records, material deliveries, change orders, schedule variance tracking, quality observations, risk resolutions.

Phase 4 (Close-Out): punch list, final inspections, certificate of occupancy, project financial reconciliation, lessons learned extraction.

At close-out, the Brain does not shut down — it becomes a historical record that informs future projects of the same type, in the same market, with the same trades.

---

## 3.2 Current Implementation (✅ Implemented)

**Service**: `services/project_brain/` — `routes.py` + `intelligence.py`
**Mounted at**: `/api/v1/services/project-brain`

### Implemented Endpoints

| Endpoint | Description | Response Time |
|----------|-------------|--------------|
| `GET /{id}/intelligence` | Full snapshot — all data sources | ~1-2s |
| `GET /{id}/health` | RED/YELLOW/GREEN + risk counts | ~200ms |
| `GET /{id}/risks` | Detected risk patterns with evidence | ~500ms |
| `GET /{id}/summary` | AI narrative + actions (Haiku) | ~3-5s |
| `GET /{id}/health-history?days=N` | Trending health snapshots | ~200ms |

### Project Brain Snapshot Schema

```sql
TABLE project_brain_snapshots (
    project_id         INTEGER,
    snapshot_date      DATE,
    health             TEXT,            -- GREEN / YELLOW / RED
    health_factors     JSONB,           -- what drove the health score
    risk_count         INTEGER,
    budget_exposure    NUMERIC,
    schedule_variance_days INTEGER,
    open_decisions     INTEGER,
    open_bids          INTEGER,
    ai_summary         TEXT,            -- Claude Haiku narrative
    data_completeness_pct NUMERIC,
    UNIQUE (project_id, snapshot_date)
)
```

### Intelligence Response Structure

```json
{
  "project_id": 1,
  "project_name": "64 Eastwood",
  "health": "YELLOW",
  "health_factors": ["19 open bid packages", "0 schedule items"],
  "risks": [
    {
      "risk_code": "PROC-001",
      "risk_type": "procurement",
      "severity": "high",
      "title": "Bid invitations sent without response",
      "evidence": "...",
      "confidence": 0.85,
      "mitigation": "..."
    }
  ],
  "risk_summary": {"critical": 0, "high": 1, "medium": 2, "low": 0},
  "decisions": [...],
  "timeline": {...},
  "procurement": {...},
  "missing_information": [...],
  "open_questions": [...],
  "data_completeness_pct": 75.0,
  "data_sources": {...}
}
```

---

## 3.3 Project Brain Components — Implementation Map

### 3.3.1 Memory (✅ Partial)
- `project_brain_snapshots` — daily health + risk snapshots
- `project_risks_computed` — detected risk records with lifecycle
- `background_learning_records` — documents processed per project

### 3.3.2 Events (✅ BTW-4 Extended Memory — Added 2026-06-29)
- `project_events` table — 373 events across 13 types (daily_log, award, rfi_submitted, meeting, risk_identified, submittal, change_order, field_note, decision, milestone, personnel, budget)
- `GET /gateway/project/{code}/timeline` — returns chronological events with filters (`?days=N&event_type=X`)
- Events auto-backfilled from: `daily_logs`, `rfis`, `risks`, `submittals`, `bid_entries`

### 3.3.3 Timeline
✅ `intelligence.py:_timeline()` — constructs timeline from schedule_variance, submittals, rfis, decisions

### 3.3.4 Knowledge Graph (✅ BTW-9 — Implemented)
- `services/knowledge_graph/graph.py` — entity nodes + relationship edges (in-memory, rebuilt on demand)
- Nodes: projects, vendors, subcontractors, contacts, RFIs, change orders, purchase orders, bids
- Edges: worked_on, supplied_to, submitted_on, raised_on, bid_on
- Endpoints: `GET /api/v1/services/knowledge-graph/vendor`, `/issues`, `/product`, `/graph`, `/summary`
- Qdrant semantic layer: vendor_memory (2,880 pts), drive_memory (2,347 pts), project_memory (2,690 pts)

### 3.3.5 Decisions
✅ `executive_inbox` table — pending decisions with approve/reject/defer tokens

### 3.3.6 Risks
✅ `project_risks_computed` — auto-detected risks per project with severity, evidence, confidence

### 3.3.7 Vendors
✅ `bid_entries` + `vendors` — bid activity and awards per vendor per project

### 3.3.8 Communications
✅ `rfis`, `submittals`, `meetings`, `executive_inbox` — tracked but not unified

### 3.3.9 Budget
✅ `houzz_budget`, `houzz_change_orders`, `historical_cost_records` — budget intelligence (awaiting Houzz extraction)

### 3.3.10 Schedule
✅ `houzz_schedule_items`, `schedule_variance` — schedule intelligence (awaiting Houzz extraction)

### 3.3.11 Documents
✅ `background_learning_records` — discovered documents from Drive/Outlook

### 3.3.12 Photos
⚠️ *Not yet implemented — Houzz photo API available*

### 3.3.13 Lessons Learned
✅ `lessons_learned` table — structured lessons per project

### 3.3.14 AI Reasoning
✅ `BaseIntelligenceService.ask_claude()` — Haiku for fast synthesis; used in `/{id}/summary`

### 3.3.15 Confidence Scoring
✅ `predictions_computed.confidence` — 0.0 to 1.0 float per prediction type

### 3.3.16 Cross-Project Relationships
✅ `services/cross_project/routes.py` — vendor overlap, procurement comparison, schedule trends

### 3.3.17 Future Evolution
*[Chief Architect: Define how the Project Brain should grow over time]*

---

## 3.4 Class Architecture (✅ Implemented)

```
BaseIntelligenceService
    │
    └── ProjectIntelligenceEngine (services/project_brain/intelligence.py)
            ├── health()
            ├── detect_risks()
            │       ├── _procurement_risks()
            │       ├── _schedule_risks()
            │       ├── _decision_risks()
            │       ├── _budget_risks()
            │       └── _data_gap_risks()
            ├── intelligence()
            ├── summary()
            └── _persist_snapshot()
```

---

---

## 3.5 BTW-4 Extended Memory — Full Endpoint Map (Added 2026-06-29)

| Endpoint | Table | Description |
|----------|-------|-------------|
| `GET /gateway/project/{code}/timeline` | `project_events` | 373 chronological events, 13 types |
| `GET /gateway/project/{code}/documents` | `project_document_links` | Documents linked to decisions/risks/COs |
| `GET /gateway/project/{code}/memory` | `project_ai_conversations` | AI conversation history per project |
| `POST /api/v1/services/project-brain/{id}/query` | writes to conversations | Ask any question about the project |
| `GET /gateway/project/{code}/brain` | `project_brain_snapshots` | Full daily snapshot |
| `GET /api/v1/services/continuous-discovery/detect` | `connector_sync_state` | Change detection pipeline |

---

## 3.6 Risk Detection Methodology
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### How the System Detects Risks

Risk detection in the HCI AI OS is algorithmic, consistent, and continuous. It runs on every project, every night, and on-demand. Unlike human risk review — which depends on who is reviewing and what they happen to notice — the system applies the same detection logic to every project, every time.

**Procurement Risk Algorithm:** For each bid package, zero bids received flags a procurement gap. If that package sits on the critical path, or the deadline is under 7 days, severity is CRITICAL regardless of other factors. 7–21 days out is HIGH; beyond 21 days is MEDIUM. If total bid coverage across a project falls below 30%, that becomes a portfolio-level HIGH risk on its own.

**Schedule Risk Algorithm:** Variance = (current projected − baseline) / baseline. Variance over 20% on a critical-path item is CRITICAL; over 20% off the critical path is HIGH. 10–20% on critical path is HIGH, off critical path is MEDIUM. Under 10% is within tolerance — no flag.

**Decision Bottleneck Algorithm:** A critical-priority approval queue item pending over 24 hours is CRITICAL. A high-priority item pending over 72 hours is HIGH. An RFI open more than 14 days without response is HIGH. A submittal pending review more than 21 days is MEDIUM.

**Data Gap Algorithm:** No contract value set is MEDIUM (limits budget risk assessment). No schedule items at all is HIGH (no schedule intelligence possible). A connector unsynced more than 48 hours is HIGH (stale data risk).

**Confidence Scoring for Risk Detection:** Full, freshly-synced, multi-signal data yields 0.8–1.0 confidence. Most data present, sync under 24 hours, single signal: 0.5–0.8. Some gaps, sync 24–48 hours: 0.3–0.5. Significant gaps, stale data: 0.1–0.3. A CRITICAL risk at 0.3 confidence should trigger investigation and data refresh, not immediate escalation — severity and confidence are reported together for exactly this reason.

**The Non-Duplication Rule:** If the same risk condition is detected on consecutive scans, the system updates the existing risk record's last-detected timestamp rather than creating a new risk. This prevents the approval queue from being flooded with duplicate alerts.

**Risk Suppression:** When Buck explicitly acknowledges a risk as accepted (e.g., a bid total running over budget by design, under active negotiation), that acknowledgment is stored. The system does not re-surface the risk at CRITICAL severity on the next scan — it moves to ACKNOWLEDGED and is monitored for status change, not re-alarmed.

---

*Ref: [architecture/PROJECT_BRAIN_SPEC.md](../architecture/PROJECT_BRAIN_SPEC.md)*
