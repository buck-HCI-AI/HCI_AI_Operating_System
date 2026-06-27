# Volume IV — Role Intelligence
*HCI AI Construction Operating System Architecture Handbook*
**Covers: Superintendent Console / Project Manager Console / Leadership Dashboard**

---

> **Authorship Split:**
> Section 4.1–4.3 (Philosophy): ⚠️ Chief Architect Required
> Section 4.4–4.9 (Implementation Reference): Claude Code

---

## 4.1 Role-Based Intelligence Philosophy (⚠️ Chief Architect Required)

*[Chief Architect: Why does each role need different intelligence?
What is the cognitive model for each role — what do they need to see, decide, and do?]*

---

## 4.2 Superintendent Operating Model (⚠️ Chief Architect Required)

*[Chief Architect: How should a Superintendent interact with AI intelligence?
What decisions remain human? What is AI's role on the job site?]*

---

## 4.3 Project Manager Operating Model (⚠️ Chief Architect Required)

*[Chief Architect: How should a PM use AI intelligence for weekly reviews and procurement?
What is the PM's approval authority within the AI system?]*

---

## 4.4 Superintendent Daily Console — Implementation Reference

**Endpoint:** `GET /api/v1/superintendent/{project_id}/today`

**Sections delivered:**
1. Schedule status (today's tasks, overdue items, completion %)
2. Safety topics (OSHA-relevant daily topics by trade)
3. Weather + field conditions
4. Active subcontractors on site
5. Open RFIs and submittals
6. Daily log status + AI draft
7. Punch list items due
8. Tomorrow's look-ahead

**Data sources:** `houzz_schedule_items`, `houzz_daily_logs`, `houzz_tasks`, `project_risks_computed`

**Mobile experience:** Single-scroll design; touch-optimized for field tablet use

---

## 4.5 Superintendent Safety Topics

Auto-selected by active trade (from `houzz_subcontractors` + `houzz_schedule_items`):

| Trade | Key Topics |
|-------|-----------|
| Concrete | Fall protection, rebar caps, formwork collapse |
| Framing | Fall protection, saw safety, caught-in hazards |
| Electrical | Lockout/tagout, energized work, GFCIs |
| Roofing | Fall protection, heat illness, material handling |
| Excavation | Trenching, shoring, underground utilities |

---

## 4.6 Project Manager Weekly Console — Implementation Reference

**Endpoint:** `GET /api/v1/pm/{project_id}/weekly`

**Sections delivered:**
1. Schedule health (variance from baseline, critical path items)
2. Budget health (committed vs budgeted, open change orders)
3. Procurement status (bid packages open, packages needing award)
4. Subcontractor performance (on-time delivery, RFI response time)
5. Risk register (top 5 risks this week, new risks detected)
6. Decision queue (pending decisions with recommended actions)
7. Client communication needs (items needing client response)
8. Next week priorities (AI-generated priority list)

**Priority algorithm:** `(severity × urgency × financial_impact) / days_remaining`

---

## 4.7 Leadership Dashboard — Implementation Reference

**Endpoint:** `GET /api/v1/leadership/dashboard`

**Sections delivered:**
1. Company health score (portfolio-weighted average)
2. Active project health matrix (RED/YELLOW/GREEN per project)
3. Total revenue under management
4. Cash flow position
5. Critical risks across all projects
6. Pending approvals (approval_queue)
7. AI productivity metrics (ROI log)
8. Subcontractor performance summary
9. Procurement pipeline

---

## 4.8 Console Endpoint Map

| Console | Endpoint | Refresh | Mobile |
|---------|----------|---------|--------|
| Superintendent Daily | `/superintendent/{id}/today` | Real-time | ✅ Optimized |
| PM Weekly | `/pm/{id}/weekly` | Daily refresh | 🟡 Readable |
| Leadership Dashboard | `/leadership/dashboard` | Real-time | ✅ Summary view |
| Leadership + AI | `/executive/morning-brief` | Daily 6 AM | ✅ Push |

---

## 4.9 Cross-References

- Volume III (Project Brain) — per-project health feeding console data
- Volume V (Executive Intelligence) — leadership escalation path
- Volume VII (Automation Architecture) — n8n workflows delivering console reports
- ADR-002: Per-project intelligence model
