# HCI AI — Decision Intelligence Standard

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_Business_Operating_Layer_BOOK01_Decision_KPI_Master_Directive_v1.0

---

## Purpose

This document defines the standard for the Decision Intelligence service. It specifies the data model, decision types, capture rules, API contract, and reporting requirements.

---

## Decision Record Data Model

Every decision record must include all required fields. Optional fields should be populated where applicable.

### PostgreSQL Table: `decision_records`

```sql
CREATE TABLE decision_records (
    id                  SERIAL PRIMARY KEY,
    project_id          INTEGER REFERENCES projects(id),  -- null for company-level
    decision_type       VARCHAR(20) NOT NULL,
    decision_date       DATE NOT NULL,
    decision_maker      VARCHAR(100) NOT NULL,
    approver            VARCHAR(100),
    context             TEXT NOT NULL,
    options_considered  JSONB,          -- [{option, pros, cons}]
    selected_option     TEXT NOT NULL,
    rationale           TEXT NOT NULL,
    risk_accepted       TEXT,
    cost_impact         NUMERIC(12,2),  -- positive = increase, negative = savings
    schedule_impact     INTEGER,        -- calendar days; positive = longer
    related_rfi_ids     INTEGER[],
    related_co_ids      INTEGER[],
    related_bid_ids     INTEGER[],
    related_doc_ids     TEXT[],         -- MinIO file paths
    outcome             TEXT,           -- filled at closeout
    outcome_rating      SMALLINT CHECK (outcome_rating BETWEEN 1 AND 5),
    lessons_learned     TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_decision_records_project ON decision_records(project_id);
CREATE INDEX idx_decision_records_type ON decision_records(decision_type);
CREATE INDEX idx_decision_records_date ON decision_records(decision_date);
```

---

## Decision Types

| Type Code | Description | Examples |
|-----------|-------------|---------|
| `award` | Subcontractor or vendor selection | Which concrete sub to use |
| `scope` | What to include or exclude | Include or exclude allowance item |
| `risk` | Accepting a contract or operational risk | Accept site condition as-is |
| `change` | Response to a project change | Accept, reject, or negotiate owner CO |
| `schedule` | Schedule decision | Accelerate, crash, or accept delay |
| `procurement` | Material or system selection | Substitution request |
| `team` | Personnel assignment | PM or Super assignment |
| `design` | Design or specification choice | System selection |
| `legal` | Dispute, claim, or compliance decision | Dispute a deduction |
| `lessons` | Process change based on experience | Change SOP based on post-project review |

---

## When to Create a Decision Record

A decision record is required when:
- A subcontractor is selected or rejected
- A significant scope item is included or excluded from a bid
- A contract risk is accepted in writing
- A change order is accepted, rejected, or negotiated
- A critical path schedule decision is made
- A material substitution is approved
- A PM or Superintendent is assigned to a project
- A dispute or claim decision is made
- A process change results from a post-project review

A decision record is NOT required for:
- Routine day-to-day field execution
- Minor workflow decisions with no business consequence
- Decisions already captured in other structured records (e.g., an approved CO already has a CO record)

---

## API Contract

### `POST /api/v1/decisions/`
Create a decision record.

```json
{
  "project_id": 2,
  "decision_type": "award",
  "decision_date": "2026-06-25",
  "decision_maker": "Buck Adams",
  "approver": "Buck Adams",
  "context": "Bid leveling for concrete scope complete. Three bids received.",
  "options_considered": [
    {"option": "Miller Concrete - $142,000", "pros": "Lowest price, known quality", "cons": "Tight schedule"},
    {"option": "Summit Concrete - $149,000", "pros": "No schedule qualifications", "cons": "Higher price"},
    {"option": "Alpine Concrete - $156,000", "pros": "Most experienced crew", "cons": "Highest price"}
  ],
  "selected_option": "Miller Concrete - $142,000",
  "rationale": "Miller's schedule qualification was reviewed - they can meet our pour dates with crew adjustment. Best value given quality track record.",
  "risk_accepted": "Miller may need crew augmentation for back-to-back pour days; PM to confirm pre-award.",
  "cost_impact": 142000,
  "schedule_impact": 0
}
```

### `GET /api/v1/decisions/{project_id}`
Get all decisions for a project, ordered by date descending.

### `GET /api/v1/decisions/search?q={query}&project_id={id}`
Semantic search across decision records. If `project_id` is omitted, searches all projects.

### `PATCH /api/v1/decisions/{id}/outcome`
Update a decision record with outcome after project close.

```json
{
  "outcome": "Miller performed as expected. Pour dates were met. No rework.",
  "outcome_rating": 5,
  "lessons_learned": "Miller is a reliable concrete sub when schedule is confirmed pre-award."
}
```

---

## Qdrant Integration

Decision records are embedded and stored in Qdrant for semantic search:

- **Collection:** `decision_records`
- **Text embedded:** `context` + `selected_option` + `rationale` + `risk_accepted`
- **Metadata stored:** `decision_type`, `project_id`, `decision_date`, `decision_maker`, `outcome_rating`
- **Search use:** "What concrete subs have we used on projects with tight schedules?" → returns matching decisions

---

## Reporting

Decision records are surfaced in:
- Project Brain Q&A: "What decisions were made on this project?"
- Executive dashboard: decisions requiring Buck review (outcome_rating not yet set)
- Post-project review: all decisions for the project, grouped by type
- Cross-project: "Show all `award` decisions in the last 2 years with outcome_rating ≥ 4"

---

*Service: `03_Source_Code/services/decision_intelligence/`*  
*BOOK_01 Volume 12: `BOOK_01/12_DECISION_INTELLIGENCE.md`*  
*Related: `docs/BUSINESS_PROCESS_LIBRARY.md`*
