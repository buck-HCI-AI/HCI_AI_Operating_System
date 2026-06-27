# Volume III — Project Brain
*HCI AI Construction Operating System Architecture Handbook*

---

## 3.1 What Is the Project Brain? (⚠️ Chief Architect Vision Required)

*[Chief Architect: Define the Project Brain as a persistent, intelligent memory system per project.
Describe how it should accumulate knowledge, build a timeline, and reason about a project's state.]*

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

### 3.3.2 Events
⚠️ *Platform events table exists (`platform_events`) but not yet wired to Project Brain*

### 3.3.3 Timeline
✅ `intelligence.py:_timeline()` — constructs timeline from schedule_variance, submittals, rfis, decisions

### 3.3.4 Knowledge Graph
⚠️ *[Chief Architect: Define the knowledge graph structure for cross-entity relationships]*

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

*Ref: [architecture/PROJECT_BRAIN_SPEC.md](../architecture/PROJECT_BRAIN_SPEC.md)*
