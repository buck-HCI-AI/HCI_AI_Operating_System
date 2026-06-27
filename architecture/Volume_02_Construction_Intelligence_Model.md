# Volume II — Construction Intelligence Model
*HCI AI Construction Operating System Architecture Handbook*

---

> **Authoring Note**: Philosophy and design intent sections marked ⚠️ require Chief Architect input.
> Implementation references (marked ✅) are maintained by Claude Code and synchronized with live code.

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

## 2.5 ⚠️ Chief Architect Sections

### 2.5.1 Why Construction Intelligence Is Different
*[Chief Architect: Explain the domain-specific reasoning required for construction vs generic AI]*

### 2.5.2 How the System Should Prioritize Competing Signals
*[Chief Architect: When schedule, budget, and procurement risks conflict — which takes precedence?]*

### 2.5.3 Confidence Thresholds for Autonomous Action
*[Chief Architect: At what confidence level should the system act vs flag for human review?]*

---

*Ref: [architecture/CONSTRUCTION_INTELLIGENCE_MODEL.md](../architecture/CONSTRUCTION_INTELLIGENCE_MODEL.md)*
