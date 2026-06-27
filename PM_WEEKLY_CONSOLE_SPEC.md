# PM Weekly Console — Specification
## HCI AI Operating System

**Authority:** Job Operations Intelligence Layer Directive  
**Owner:** Buck Adams  
**Status:** Spec — ready for Sprint 3 implementation  

---

## Purpose

The PM console answers one question every Monday morning: **What do I need to manage on this job this week?**

Delivered as:
- API response at `GET /api/v1/pm/{project_id}/weekly`
- Push notification Monday 07:00 via ntfy
- Email summary Monday 07:15
- Mobile-first HTML page at `/pm/{project_id}`

---

## Console Sections

### 1. Schedule Variance
```
Source: houzz_schedule_items + project_brain (baseline schedule)
Fields: planned_completion, current_forecast, variance_days, critical_path_items
Alert: variance > 3 days → YELLOW; > 7 days → RED
Lookahead: next 2 weeks of schedule items
```

### 2. Budget / Cost Exposure
```
Source: houzz_budget + historical_cost
Fields: original_budget, committed_cost, cost_to_complete, projected_final, variance_$, variance_%
Alert: over budget any line item → flag with amount
Pending: POs not yet committed (from houzz_purchase_orders)
```

### 3. Open RFIs
```
Source: houzz_tasks WHERE task_type='RFI' AND status!='complete'
Fields: rfi_number, subject, submitted_date, days_open, ball_in_court, blocking_scope
Alert: RFIs open >5 business days → escalate path
Sort: days_open DESC
```

### 4. Open Approvals
```
Source: executive_inbox WHERE status='pending' + approval_queue WHERE status='pending'
Filter: linked to this project_id
Fields: exec_id, title, deadline, confidence, required_by
Actions: approve/defer links (direct from console)
```

### 5. Bid / Procurement Status
```
Source: bid_intelligence + houzz_purchase_orders
Fields: scope, vendor, bid_amount, status, award_decision, outstanding_bids
Alert: bids expiring this week → flag for award decision
Pending: procurement items with no PO yet
```

### 6. Change Order Exposure
```
Source: houzz_change_orders
Fields: co_number, description, amount, status, signed, impact_on_schedule
Total: approved, pending, potential
Alert: unsigned COs > 30 days old
```

### 7. Vendor Risks
```
Source: houzz_vendors + houzz_subcontractors + vendor_registry
Fields: vendor_name, risk_flag, performance_score, open_issues
Risk triggers: payment dispute, no-show, behind on scope, no certificate of insurance
```

### 8. Client Communication Needs
```
Source: HubSpot activities + Outlook emails (when connector built)
Fields: last_client_contact_date, open_action_items, pending_responses
Alert: no client contact >7 days → flag
Draft: AI-drafted check-in email for PM review (Gate E required to send)
```

### 9. Outstanding Decisions
```
Source: executive_inbox + approval_queue + houzz_tasks WHERE status='waiting_decision'
Fields: decision_item, requested_by, days_waiting, blocking_impact
Sort: days_waiting DESC
Actions: route to approval with one tap
```

### 10. Next Week Priorities
```
Source: AI synthesis across all sections above
Format: ranked list of 5 most important PM actions next week
Logic: overdue > financial exposure > schedule risk > client issues > vendor risk
```

---

## API Response Shape

```json
{
  "project_id": 1,
  "project_code": "101F",
  "project_name": "101 Francis",
  "week_of": "2026-06-27",
  "generated_at": "2026-06-27T07:00:00Z",
  "health": "YELLOW",
  "schedule": {
    "variance_days": 2,
    "health": "YELLOW",
    "critical_path_items": [...],
    "lookahead_14d": [...]
  },
  "budget": {
    "original": 1250000,
    "committed": 890000,
    "cost_to_complete": 420000,
    "projected_final": 1310000,
    "exposure": 60000,
    "health": "RED"
  },
  "rfis": { "open_count": 3, "overdue_count": 1, "items": [...] },
  "approvals": { "pending_count": 2, "items": [...] },
  "procurement": { "bids_expiring": 1, "outstanding_pos": 2, "items": [...] },
  "change_orders": { "approved_total": 45000, "pending_total": 28000, "items": [...] },
  "vendor_risks": { "at_risk_count": 1, "items": [...] },
  "client_comms": { "days_since_contact": 3, "open_items": 1, "draft_checkin": "..." },
  "outstanding_decisions": { "count": 2, "items": [...] },
  "next_week_priorities": [
    "1. Resolve budget overrun on electrical scope ($60k exposure)",
    "2. Award roofing bid — 2 offers expiring Friday",
    "3. Client check-in overdue — last contact June 20",
    "4. Sign change order CO-003 ($28k, 32 days unsigned)",
    "5. RFI-007 blocking framing — 8 days open, escalate to architect"
  ]
}
```

---

## Mobile HTML View

Route: `GET /pm/{project_id}` (HTML response)

Layout:
- Summary card at top: Health / Schedule / Budget / Decisions
- Expandable sections per console item
- "Approve" action buttons directly in approval section
- "Draft Email" → opens Gate E pre-filled with client check-in draft
- "Award Bid" → opens Gate F with bid details pre-filled

---

## Automation

```
n8n: AUTO-PM-WEEKLY (new workflow)
Cron: Monday 07:00, all active projects
For each project:
  1. GET /pm/{project_id}/weekly
  2. Format push: "101F: $60k exposure, 3 open RFIs, 2 decisions needed"
  3. ntfy push to Buck + PM email
  4. If decisions >3 → also escalate to executive_inbox
```
