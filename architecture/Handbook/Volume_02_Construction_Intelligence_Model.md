# Volume II — Construction Intelligence Model
*HCI AI Construction Operating System Architecture Handbook*

---

> **Authoring Note**: Sections 2.5–2.7 (philosophy) authored by Chief Architect (ChatGPT) + Browser Claude, 2026-06-30, recovered from Google Drive and integrated 2026-07-02. Implementation references (marked ✅) are maintained by Claude Code and synchronized with live code.

---

## 2.1 Intelligence Architecture

### Four-Layer Model (✅ Implemented)

```
┌──────────────────────────────────────────────────────────────────┐
│  LAYER 4 — PREDICTIVE INTELLIGENCE                                │
│  Forward-looking risk signals with evidence + confidence scoring  │
│  schedule · budget · permit · procurement · trade · cash · inspect│
│  Endpoint: /api/v1/services/predictive-engine/{id}/predictions    │
├──────────────────────────────────────────────────────────────────┤
│  LAYER 3 — CROSS-PROJECT INTELLIGENCE                             │
│  Portfolio comparison · Company snapshot · Vendor performance     │
│  Endpoint: /api/v1/services/cross-project/company-snapshot        │
├──────────────────────────────────────────────────────────────────┤
│  LAYER 2 — PROJECT BRAIN (per-project persistent memory)          │
│  Health scoring · Risk detection · AI narrative · Snapshots       │
│  Endpoint: /api/v1/services/project-brain/{id}/intelligence       │
├──────────────────────────────────────────────────────────────────┤
│  LAYER 1 — OPERATIONAL INTELLIGENCE (role-based consoles)         │
│  SS Daily Console · PM Weekly Console · Leadership Dashboard      │
│  Endpoints: /superintendent/{id} · /pm/{id} · /leadership         │
├──────────────────────────────────────────────────────────────────┤
│  FOUNDATION — Raw Data Sources                                    │
│  Houzz · HubSpot · Outlook · Google Drive · Manual entry          │
└──────────────────────────────────────────────────────────────────┘
```

### Intelligence Data Flow (✅ Implemented)

```
External Sources
      │
      ▼
Connectors (n8n + API)
      │
      ▼
PostgreSQL (73 tables)  ◄──── Background Learning / Mining
      │
      ├──► Project Brain Snapshots (daily)
      │
      ├──► Predictions Computed (per-request)
      │
      ├──► Company Intelligence Snapshots (daily)
      │
      └──► Role Consoles (real-time)
                │
                └──► ntfy Push Notifications
```

---

## 2.2 Health Scoring Algorithm (✅ Implemented)

**Implementation**: `services/project_brain/intelligence.py:_compute_health()`

```
RED    ← any risk with severity = "critical"
YELLOW ← any risk with severity = "high" (but no critical)
GREEN  ← no critical or high risks
```

**Risk codes currently detected**:

| Code | Type | Description | Threshold |
|------|------|-------------|-----------|
| PROC-001 | procurement | Open bids >14 days no response | 14 days |
| PROC-002 | procurement | Open bid packages (any) | > 0 |
| PROC-003 | procurement | Pending approval queue items | > 10 |
| SCHED-001 | schedule | High-risk variance items | risk_level = 'high' |
| SCHED-002 | schedule | Critical variance items | risk_level = 'critical' |
| SCHED-003 | schedule | Average variance | > 7 days |
| BUDGET-001 | budget | Historical cost overrun | avg variance_pct > 15% |
| BUDGET-002 | budget | Committed > budget | committed > budgeted |
| DEC-001 | decision | Stale pending decisions | > 3 days old |
| DATA-001 | data | Low data completeness | < 60% |

---

## 2.3 Prediction Models (✅ Implemented)

**Implementation**: `services/predictive_engine/routes.py`

Seven prediction types, each returns:
- `risk_level`: HIGH / MEDIUM / LOW / CLEAR
- `confidence`: 0.0 – 1.0 (float)
- `confidence_label`: High / Medium / Low
- `evidence`: list of `{item, weight}` objects
- `predicted_impact`: human-readable impact statement
- `recommended_actions`: list of specific action items
- `data_sources`: tables queried

| Type | Primary Data Sources | Confidence Range |
|------|---------------------|-----------------|
| schedule | schedule_variance, submittals, rfis, long_lead_items | 0.25 – 0.85 |
| budget | houzz_budget, houzz_change_orders, bid_packages, historical_cost_records | 0.25 – 0.85 |
| permit | submittals, executive_inbox, approval_queue | 0.20 – 0.75 |
| procurement | bid_packages, bid_entries, long_lead_items | 0.30 – 0.80 |
| trade_conflict | schedule_variance, bid_entries, rfis | 0.20 – 0.65 |
| cash_flow | houzz_budget, houzz_change_orders, approval_queue | 0.20 – 0.80 |
| inspection | submittals, rfis, schedule_variance, approval_queue | 0.20 – 0.70 |

---

## 2.4 Data Sources and Connectors (✅ Partially Implemented)

| Source | Connector Status | Tables Populated | Notes |
|--------|-----------------|-----------------|-------|
| PostgreSQL | ✅ Live | All 73 tables | Internal — always available |
| Houzz | ⚠️ Manual extraction needed | houzz_projects (3 rows) | Schedule/budget data locked — requires browser extraction |
| HubSpot | ✅ API connector | hubspot_deals, contacts, notes | Syncing |
| Microsoft Outlook | ⚠️ OAuth needed | — | n8n credential connected; connector in progress |
| Google Drive | ⚠️ OAuth needed | — | n8n credential connected; connector in progress |

---

## 2.5 Construction Intelligence Philosophy
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### Why Construction Intelligence Needs Its Own Model

Generic business intelligence assumes clean, structured data: rows in a spreadsheet, records in a CRM, transactions in an ERP. Construction data is none of these things.

Construction data is partial. Drawings evolve through revision cycles. Specifications change with substitutions. Schedules are estimates that reality constantly revises. Bids arrive at different times from different sources in different formats. A database designed to hold clean, complete records will always be partially empty in a construction project context — because construction projects are always partially in-flight.

Construction data is relational in non-obvious ways. A steel package bid is connected to the schedule item for steel delivery, which is connected to downstream framing tasks, which determine when rough inspections can happen, which determines the client's move-in date. No single record captures this chain. Intelligence requires following it.

Construction data is expert-dependent. Whether a particular RFI response is adequate, whether a bid price is reasonable for the scope, whether a schedule compression is achievable — these judgments require domain expertise that generic analytics tools do not have. The HCI AI OS had to encode construction-specific expertise into its intelligence logic.

These realities drove several specific design decisions:

**Decision 1: Intelligence runs on partial data.** The system does not wait for complete data before generating intelligence. It runs on what it has, reports its confidence level based on completeness, and flags the specific gaps. A project in week one with minimal data gets useful intelligence — it just comes with lower confidence and explicit flags for what's missing. This is more valuable than silence.

**Decision 2: Evidence is the primary output.** The system was designed to produce evidence, not just conclusions. The person who makes the decision bears the accountability, and they need to understand the basis for the recommendation.

**Decision 3: Domain expertise is encoded in detection logic.** The risk detection algorithms encode construction-specific expertise: what a bid coverage rate means at different project phases, what schedule variance on a critical-path task means for downstream dependencies, what it means when the only bid for a trade package is well above estimate.

**Decision 4: The system admits what it doesn't know.** Low confidence scores, data gap flags, explicit "no data available" responses — these are features, not failures. A system that fabricates high-confidence answers when data is thin is actively dangerous. The HCI AI OS is calibrated to be honest about the quality of its own intelligence.

---

## 2.6 Data Flow Philosophy
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### How Data Moves Through the System

Data in the HCI AI OS flows through four stages: collection, normalization, intelligence, and presentation. Each stage has a clear responsibility and clear interfaces with adjacent stages.

**Stage 1: Collection (Connectors)** — Connectors pull data from external sources on schedule or on event. Each connector is responsible for exactly one data source and does not perform intelligence — it translates external data into the canonical data model. Every connector maintains a sync state record: last successful sync, records synced, errors encountered. A connector that has not synced in 24 hours is a data freshness risk, surfaced in the health brief.

**Stage 2: Normalization (Data Services)** — Before intelligence can run, data must be normalized: date format standardization, currency conversion, name deduplication (the same subcontractor appearing under two spellings in different documents), and status vocabulary standardization. Normalization flags anomalies for review rather than silently correcting them.

**Stage 3: Intelligence (Services Layer)** — Normalized data flows into the intelligence services. Each service operates on a clean, standardized data representation and produces a structured intelligence output. Services are read-only — they do not modify the normalized data they consume. Intelligence outputs are cached with a TTL appropriate to the data's rate of change; the Project Brain snapshot is rebuilt on each request to ensure recency.

**Stage 4: Presentation (Role Consoles)** — Intelligence outputs are assembled into role-specific views. The presentation layer does not perform intelligence — it selects, formats, and prioritizes the intelligence outputs most relevant to each role's decision-making context. When a significant event occurs, the relevant role console data is invalidated and rebuilt via the n8n workflow engine.

**The principle of canonical source:** For any given data element, there is exactly one source of truth. Bid amounts live in the bids table — nowhere else. Schedule variances are computed from the schedule items table — not from manually entered summaries. If two sources disagree, the canonical source wins, and the discrepancy is flagged.

---

## 2.7 Risk Classification Model
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### How HCI Defines, Measures, and Responds to Risk

Construction risk management has historically been informal: an experienced PM has a gut feeling that something is going wrong, escalates it, and it gets handled. This works — when the experienced PM is available, paying attention, and has enough bandwidth to catch every signal. The HCI AI OS formalizes risk management without making it bureaucratic: it defines exactly what makes a risk critical, high, medium, or low, so the system can apply that judgment consistently, at scale, 24/7.

**Risk Categories:**

*Procurement Risk* — A trade package has insufficient bid coverage and/or is approaching a bid deadline without closure. This is systemic: a gap in one trade's coverage affects schedule, budget, and downstream coordination, not just that one package.

*Schedule Risk* — A task is running behind baseline, particularly if that task is on the critical path or has downstream dependencies. Schedule risk compounds quickly: a short delay on one critical-path task can become a much longer project delay if it cascades through dependencies.

*Budget Risk* — The total committed or estimated cost for a project scope is exceeding the contract value or budget estimate. It can emerge from bid results, from change orders, or from allowance overruns.

*Decision Bottleneck* — An action item requiring human decision has been pending beyond an acceptable threshold. Bottlenecks create cascading delay: an unanswered RFI blocks a trade from proceeding, which blocks a downstream trade, which compresses the schedule.

*Data Gap* — A record is missing information the intelligence system needs to produce accurate output. Data gaps are risks because they make the system less able to detect the other risk types.

**Severity Classification:**

*Critical* — Immediate action required within 24–48 hours. *High* — Action required within 7 days. *Medium* — Monitor and schedule a response. *Low* — Logged and visible, not driving urgent action.

**The Confidence-Severity Relationship:** A critical risk with 0.9 confidence demands immediate action. A critical risk with 0.4 confidence demands investigation — verify the risk is real before escalating. The system reports both severity and confidence together, precisely because severity alone is incomplete information.

**Risk Lifecycle:** DETECTED → OPEN (system detects and logs) → ACKNOWLEDGED (human sees and confirms) → IN RESPONSE (action underway) → RESOLVED (risk eliminated or accepted) → CLOSED. Resolution notes are required when closing a risk and feed the lessons-learned corpus.

**Risk Escalation:** Risks that remain OPEN beyond their escalation threshold (24 hours for critical, 7 days for high) are automatically re-surfaced in the morning brief with an OVERDUE flag. This prevents risks from being acknowledged and then forgotten.

---

*Ref: [architecture/CONSTRUCTION_INTELLIGENCE_MODEL.md](../architecture/CONSTRUCTION_INTELLIGENCE_MODEL.md)*
