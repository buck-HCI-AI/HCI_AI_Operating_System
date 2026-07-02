# Volume V — Executive Intelligence
*HCI AI Construction Operating System Architecture Handbook*
**Covers: Executive Mission Control / Morning Brief / Approval Workflow**

---

> **Authorship Split:**
> Section 5.1–5.2 (Philosophy): Chief Architect (ChatGPT) + Browser Claude, 2026-06-30, recovered from Google Drive and integrated 2026-07-02
> Section 5.3–5.8 (Implementation Reference): Claude Code

---

## 5.1 Executive Intelligence Philosophy
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### How Buck Adams Wants to Use AI

Buck Adams does not want to use software. He wants to run a construction company. The HCI AI OS serves him best when it is invisible: when it handles the information management work so completely that Buck's experience is "I always know what's happening and I always know what to do next" — without consciously thinking about the system behind it.

**The 5-minute principle:** Every morning, Buck should be able to review the complete state of all active projects, identify the things that require his decision today, and queue those decisions — in five minutes or less. If the Owner Console requires more than five minutes to process, it has too much information, is poorly organized, or is not prioritizing effectively.

**Action first, summary second:** The Owner Console leads with actions — decisions pending, risks requiring response, approvals in queue. The portfolio health summary comes after. Buck does not need to read a summary to know whether to act; he needs to know what to act on, and can read the context after.

**Time budget model:** Buck's engagement with the system is budgeted at roughly 15 minutes a day across morning review, afternoon check, and approval processing. If the system is generating more action items than can be processed in that window, it is generating too much noise, and sensitivity thresholds need adjustment.

**Mobile-first:** Buck reviews the system from his phone as often as from a desktop. The Owner Console and ntfy notifications are the primary interface; anything requiring a desktop is secondary.

**The trust threshold:** Buck will trust AI-generated intelligence when it is consistently accurate and the evidence is always visible. If the system ever presents a confident assertion that turns out to be wrong, and the evidence trail doesn't make clear why, trust degrades. Every intelligence output must be traceable.

---

## 5.2 Approval Authority Model
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### The Complete Approval Authority Matrix

The approval authority matrix is the operational implementation of "AI proposes, humans decide." It defines, for every category of action, what level of authorization is required and who provides it.

**Tier 0: Fully Automated (no approval required)** — Generating morning briefs, daily reports, health summaries; detecting risks, bid gaps, schedule variances (detection only, not response); indexing new documents; running nightly audits; refreshing role console data; logging project events to the Brain.

**Tier 1: Buck's Approval Required (via approval queue + ntfy)** — Sending any external communication (email, RFI to design team, client update); drafting any SOW for subcontractor review; any bid award recommendation; any change order recommendation to a client; any commitment to a trade partner (hold dates, delivery commitments); any communication to a permitting authority; writing data back to HubSpot.

**Tier 2: Buck's Direct Action Required (AI assists only)** — Signing contracts or legal documents; authorizing financial payments or wire transfers; any personnel decision; disclosing project financial data externally; approving design alternatives requiring engineering signoff.

**PM Authority (within their project scope)** — PMs may approve routine subcontractor coordination communications (not awards), RFI routing to the design team, submittal routing and review requests, field note acknowledgment, and standard inspection scheduling. PMs route to Buck when the action involves a financial commitment above their authority threshold, a client commitment, a design change with cost implications, or anything outside project scope or budget without owner approval.

**Escalation Path:** Critical risk → Buck, phone call within 2 hours. High risk → Buck via approval queue, ntfy alert at 24 hours. Medium risk → PM console, escalates to Buck at 7 days. Low risk → PM awareness, no escalation.

**Approval Queue Mechanics:** Every Tier 1 item enters the approval queue with a title, full context/evidence/recommended action, priority, requester, a decision deadline based on priority, and status (pending/approved/rejected/deferred/expired). Items that pass their deadline without action are auto-escalated: status set to "escalated," ntfy push sent, and the morning brief flags it OVERDUE.

**The Anti-Flood Rule:** No more than roughly 5 new items should enter the approval queue from automated detection in any given 24-hour period, except during active escalation events. If detection is generating more than that on average, sensitivity thresholds are miscalibrated. The approval queue is a decision surface, not a notification log — if it becomes overwhelming, it stops being used, and governance breaks down.

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
