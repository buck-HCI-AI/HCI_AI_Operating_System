# Volume V — Executive Intelligence
*HCI AI Construction Operating System Architecture Handbook*
**Covers: Executive Mission Control / Morning Brief / Approval Workflow**

---

> **Authorship Split:**
> Section 5.1–5.2 (Philosophy): ⚠️ Chief Architect Required
> Section 5.3–5.8 (Implementation Reference): Claude Code

---

## 5.1 Executive Intelligence Philosophy (⚠️ Chief Architect Required)

*[Chief Architect: What decisions does Buck Adams need AI to support vs make?
What is the morning intelligence briefing model — what does Buck see first thing each day?
How does executive intelligence differ from operational intelligence?]*

---

## 5.2 Approval Authority Model (⚠️ Chief Architect Required)

*[Chief Architect: Define the approval authority matrix.
What can AI recommend? What can AI act on autonomously? What requires Buck's explicit approval?
What is the time budget for Buck's daily AI interaction?]*

---

## 5.3 Executive Mission Control — Implementation Reference

**Endpoint:** `GET /api/v1/executive/mission-control`

**11 data sections:**

| Section | Data Source | Description |
|---------|-------------|-------------|
| `company_health` | `company_intelligence_snapshots` | Portfolio-level RED/YELLOW/GREEN |
| `portfolio` | `project_brain_snapshots` | Per-project health + trends |
| `ai_missions` | `missions` | Active AI missions + status |
| `ai_productivity` | `roi_log` (30 days) | Minutes saved, documents processed |
| `pending_approvals` | `approval_queue` | Items needing Buck's action |
| `critical_alerts` | `predictions_computed` (HIGH risk) | Forward-looking HIGH risk predictions |
| `top_risks` | `project_risks_computed` | Critical + high severity risks |
| `top_opportunities` | `autonomy_opportunities` | Automation opportunities by ROI |
| `weekly_trends` | `project_brain_snapshots` (28 days) | Health trend per project |
| `kpi_dashboard` | `kpi_snapshots` | Key performance indicators |
| `procurement_pulse` | `bid_packages` | Open bid packages needing action |

---

## 5.4 Morning Brief — Implementation Reference

**Endpoint:** `GET /api/v1/executive/morning-brief`

Auto-delivered daily via n8n at 6:00 AM MST via ntfy push to `hci-executive`.

**Content:** Company health summary, 3 most urgent items, 3 biggest risks, today's decisions needed.

---

## 5.5 Approval Workflow — Implementation Reference

```
Risk/Decision Detected (Project Brain or Predictive Engine)
    ↓
approval_queue INSERT (status='pending', workflow='...', target_description='...')
    ↓
Morning Brief includes pending_approvals count
    ↓
Buck reviews via Mission Control dashboard
    ↓
Buck approves/rejects (manual API call or future mobile UI)
    ↓
GATE-H n8n workflow executes approved action
    ↓
approval_queue UPDATE (status='approved'/'rejected', actioned_at=NOW())
```

**Approval gate types:**
- `hubspot_write` — CRM update
- `drive_upload` — Google Drive write
- `bid_import` — bid package data
- `daily_log` — AI-drafted daily log
- `client_comms` — any client-facing communication
- `financial` — budget/change order actions

---

## 5.6 Predictive Engine — Implementation Reference

**Endpoint:** `GET /api/v1/services/predictive-engine/{project_id}/predictions`

**7 prediction types:**

| Type | Risk Category | Key Signals |
|------|--------------|-------------|
| `schedule` | Schedule slip | Task overdue count, critical path pressure |
| `budget` | Budget overrun | Change order frequency, uncommitted variance |
| `permit` | Permit delay | Active permit count, inspection backlog |
| `procurement` | Procurement delay | Open bid packages, vendor count |
| `trade_conflict` | Trade coordination failure | Concurrent trade density |
| `cash_flow` | Cash flow pressure | Approval queue age, change order status |
| `inspection` | Inspection failure | Punch list density, active trade count |

**Confidence model:** Additive evidence weighting (0.1–0.3 per signal), capped at 0.85.
See ADR-003 for full rationale.

---

## 5.7 ntfy Integration

**Topic:** `hci-executive` at `https://ntfy.sh/hci-executive`

| Trigger | Priority | Tags |
|---------|----------|------|
| Morning Brief | default | construction |
| HIGH risk prediction | high | warning |
| System audit complete | default | white_check_mark |
| Approval required | high | bell |
| BTW mission complete | default | books |

---

## 5.8 Cross-References

- Volume III (Project Brain) — health scores feeding executive dashboard
- Volume IV (Role Intelligence) — escalation path from operations to executive
- Volume VI (Construction Intelligence Engine) — risk detectors feeding approval queue
- Volume VIII (Governance) — approval authority and human override rules
- ADR-003: Confidence scoring
- ADR-004: Health scoring algorithm
