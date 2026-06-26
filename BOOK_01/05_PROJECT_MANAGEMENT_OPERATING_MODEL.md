# BOOK_01 — Volume 05: Project Management Operating Model

**Version:** 1.0 | **Date:** 2026-06-25

---

## PM Role

The Project Manager is the day-to-day owner of the project record. The PM controls:
- Budget tracking and cost coding
- Schedule maintenance
- RFI and submittal log management
- Subcontractor coordination
- Client and design team communication
- Change management
- Weekly status reporting

The PM uses HCI AI to stay ahead of the project — not to catch up to it.

---

## PM Daily Routine

| Time | Task | System Action |
|------|------|---------------|
| 7:00 AM | Read morning brief | Auto-delivered — project status, weather, schedule alert |
| Morning | Review field logs from prior day | System compiled and summarized overnight |
| Morning | Action open RFIs and submittals | RFI/submittal status list current in system |
| Mid-day | Review any flagged risks or issues | Risk log updated by AI and Superintendent |
| PM | Log coordination calls and decisions | Meeting intelligence captures notes |
| PM | Review and approve daily log summaries | Superintendent submitted; PM confirms |
| Weekly | Draft and send weekly status report | AI drafts from project data; PM reviews and sends |

---

## PM Weekly Routine

| Day | Task |
|-----|------|
| Monday | Review prior week summary; update schedule look-ahead |
| Tuesday | Subcontractor coordination calls; log all commitments |
| Wednesday | Budget review: compare posted costs to budget; flag variances > 5% |
| Thursday | Client communication; weekly update drafted |
| Friday | Sign off weekly report; review next-week priority list |

---

## Budget Control

The PM owns budget control. The system makes this automatic:

- Every cost is coded to a budget line at entry
- Variance is calculated automatically: (Budget - Committed - Posted) = Remaining
- Variances > 5% on any line trigger a yellow flag to PM
- Variances > 10% trigger a red flag to PM and Buck
- Change orders that increase budget require Buck approval before being added

**Budget entries that require human confirmation:**
- Any cost posting that exceeds the committed amount for a scope line
- Any cost transfer between budget lines
- Any budget increase (change order, allowance draw, contingency use)

---

## RFI Management

RFIs are tracked from submission to closed:

| Status | Meaning |
|--------|---------|
| Draft | PM has not yet sent |
| Submitted | Sent to design team; date logged |
| Responded | Response received; date logged; impact flagged |
| Closed | Incorporated into scope/documents |
| Overdue | No response by committed date; PM notified, Buck on CC |

AI drafts RFI text from the question, the relevant drawing reference, and the impact statement. PM reviews and sends.

**RFI response SLA:** If no response in 5 business days, system sends reminder. At 10 days, escalates to PM with recommended follow-up action.

---

## Submittal Management

Submittals follow the same status model as RFIs. The PM submits all shop drawings and product data to the design team.

Key controls:
- No material fabrication or delivery before submittal is returned "Approved" or "Approved as Noted"
- Submittals returned "Revise and Resubmit" are re-queued with new due date
- All submittal responses are logged with date, reviewer, and disposition

---

## PM KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Budget variance on open scopes | < 10% any line, < 5% total | Budget service |
| RFI response time (after HCI submission) | PM tracks; escalate at 10 days | RFI log |
| Open RFIs > 14 days | 0 | RFI age report |
| Submittal cycle time | Per schedule requirement | Submittal log |
| Change orders issued within 5 days of trigger | > 90% | CO log |
| Weekly report delivered by Friday 5 PM | 100% | Report log |

---

*Volume 06 covers the Superintendent operating model.*  
*RFI and submittal data: `rfis` and `submittals` tables in PostgreSQL.*
