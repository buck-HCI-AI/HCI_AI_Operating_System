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
*[Chief Architect: Explain the domain-specific reasoning required for construction vs generic AI]*

*Authored by: GBT Chief Architect — 2026-07-02 (verified via getMissionControl + getProjectBrain 101F)*

Construction intelligence differs from conventional business intelligence because it must combine structured operational data with incomplete, evolving project information while preserving traceability.

Within HCI AI OS, project intelligence is assembled from multiple operational sources rather than a single transactional database. Depending on project maturity, available evidence may include procurement records, bid packages, RFIs, drawings, approvals, connector synchronization, executive decisions, and project metadata.

Because projects progress through distinct lifecycle phases, the same indicator can have different meanings at different times. A project in preconstruction should not generate conclusions about field progress simply because historical schedule artifacts exist. System recommendations must therefore be interpreted in the context of the verified project lifecycle.

The platform treats verified operational state as authoritative and requires live validation before generating construction-status conclusions (ADR-016).

---

### 2.5.2 How the System Should Prioritize Competing Signals

*Authored by: GBT Chief Architect — 2026-07-02*

The intelligence engine evaluates evidence according to source reliability rather than source quantity.

**Signal priority hierarchy (highest to lowest):**
1. Live platform state (Mission Control, Project Brain, verified project records)
2. 2. Executive approvals and governance decisions
   3. 3. Structured project data (procurement, bid packages, RFIs, decisions)
      4. 4. Connector-derived operational information
         5. 5. Historical reference information
           
            6. When conflicting signals exist, the system favors the most recently verified authoritative source and records uncertainty rather than manufacturing certainty. Lower-priority or historical signals may provide context but must not override current verified operational state.
           
            7. **Example:** If a schedule artifact suggests active framing but permit_status = not_issued, the permit status overrides the schedule artifact. The schedule artifact is flagged as potentially invalid.
           
            8. ---
           
            9. ### 2.5.3 Confidence Thresholds for Autonomous Action
           
            10. *Authored by: GBT Chief Architect — 2026-07-02*
           
            11. Every architectural recommendation carries an implicit confidence assessment based on evidence quality.
           
            12. **Governance thresholds:**
           
            13. | Confidence Level | Definition | System Action |
            14. |-----------------|------------|---------------|
            15. | High | Corroborated by live operational data from authoritative sources | Surface as finding; may trigger alert |
            16. | Medium | Supported by multiple consistent sources; awaiting additional confirmation | Surface as advisory; flag for review |
            17. | Low | Based on incomplete, historical, or partially synchronized information | Surface as low-confidence observation only |
            18. | Unverified | Insufficient evidence to support a factual claim | Must not be presented as fact; label UNVERIFIED |
           
            19. Under ADR-016, unverified information must remain explicitly identified as such rather than presented as completed work or operational fact.
           
            20. **Autonomous action threshold:** The system acts autonomously only on HIGH-confidence signals where the action is within the approved autonomy list (see Volume IX Governance). All other signals surface for human review.
           
            21. ---
           
            22. Ref: architecture/CONSTRUCTION_INTELLIGENCE_MODEL.md
