# Volume IV — Role Intelligence
*HCI AI Construction Operating System Architecture Handbook*
**Covers: All 9 Role Consoles — Superintendent / Project Manager / Leadership / Owner / Office / Accounting / Client / Trade Partner / Executive**
**Last Updated: 2026-06-29 | Claude Code v3.5**

---

> **Authorship Split:**
> Section 4.1–4.3.5 (Philosophy): Chief Architect (ChatGPT) + Browser Claude, 2026-06-30, recovered from Google Drive and integrated 2026-07-02
> Section 4.4–4.9 (Implementation Reference): Claude Code

---

## 4.1 Role-Based Intelligence Philosophy
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### Why Different Roles Need Different Intelligence

The HCI AI OS has one underlying intelligence layer but nine different user interfaces. This is not a cosmetic decision — it reflects a fundamental truth about information in organizations: the same data means different things to different people, and presenting the wrong data to the wrong person wastes their time at best and creates confusion at worst.

Buck Adams needs to know which risks require his decision today. He does not need to know the exact current temperature on the job site. The superintendent needs to know who is delivering material at 7 AM. They do not need to know the change order approval status. The accountant needs to know which subcontractor invoices are pending and whether they are within the approved contract amounts. They do not need to know the structural RFI status.

The cognitive model for each role is different. Buck makes portfolio-level strategic decisions. The PM manages coordination and relationships. The superintendent manages field execution. The accountant manages financial accuracy. Each of these decision-making contexts requires different inputs, at different levels of granularity, with different urgency.

**The Design Principle:** Each role console presents exactly the information most relevant to the decisions that role makes — nothing more, nothing less. A console that buries the critical alert in a sea of non-urgent data has failed. A console that omits important context has also failed.

**The Shared Foundation:** All role consoles draw from the same underlying intelligence layer. When a risk is detected, it appears in every console that needs to know about it — not just the one that seems most relevant. The PM needs to know about the same steel delay that Buck sees in the Owner Console. Different framing, same underlying fact.

**Trust Through Consistency:** When different consoles show consistent information about the same project, it builds trust. When the Owner Console shows a risk that the PM Console doesn't mention, it erodes trust. Consistency across consoles is a design requirement, not just a nice-to-have.

---

## 4.2 Superintendent Operating Model
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### A Day in the Life of a Superintendent with AI

The superintendent is responsible for field execution: crew deployment, material handling, quality control, safety, subcontractor coordination, inspection management, and daily documentation. The AI system serves the superintendent in three ways.

**Before Work (6:00–7:00 AM)** — The Superintendent Daily Brief is delivered automatically each morning: today's crew deployment, expected material deliveries, scheduled inspections, open items from yesterday's field notes, relevant weather, and any open risks with field implications. Designed to be consumed in 60–90 seconds while the superintendent is still in their truck. It answers: "What do I need to know before I walk on site today?"

**During Work (7:00 AM–5:00 PM)** — Field Note Submission lets the superintendent record observations, quality notes, or safety issues in 30 seconds, auto-routed to the project brain and flagged for PM review if it contains an action item. RFI Submission routes a field question to the PM and design team immediately — no lost RFIs, no forgotten follow-ups. Open Items Query gives a 30-second phone check of every unresolved RFI, submittal, and action item for the project.

**After Work (5:00–6:00 PM)** — Daily report submission captures crew count by trade, work performed, materials delivered, delays and cause, and tomorrow's planned work. This feeds the project brain, populates the PM's coordination view for the next day, and creates the documentation record needed for change order substantiation if delays occur.

**What AI Does Not Do for the Superintendent:** It does not manage the job site, sequence the work, assign crew, or resolve field condition issues — those require field expertise, judgment, and relationship knowledge no AI system has. What the AI does is remove administrative burden: the superintendent does not have to compile status from multiple systems to give the PM an update. The system generates that update automatically from the superintendent's own field notes and daily reports.

---

## 4.3 Project Manager Operating Model
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

### How a PM Uses AI Every Week

The project manager's job is coordination: managing the design team, the subcontractors, the client, the budget, and the schedule — simultaneously. The PM is the information hub for the project. AI serves the PM in five areas.

**Procurement Management** — The bid leveling console shows current coverage by trade, received bids with vendor/amount/date, and gaps needing attention, assembled automatically from all incoming bids rather than pulled from spreadsheets or email.

**Client Communication** — The client communication console tracks all client-facing communications and pending client decisions, so the PM has a current, accurate summary in under 30 seconds when a client asks for an update. The system drafts communications for PM review when triggered by a detected event; it never sends autonomously.

**Action List** — The PM weekly action list is a prioritized to-do list generated from the intelligence layer: bids to follow up, RFIs awaiting response, submittals approaching deadline, pending approvals, risks flagged for PM attention. Refreshed every morning.

**Subcontractor Coordination** — The PM can pull the trade partner console for any subcontractor to see that sub's current work queue and awarded bids before a coordination call — walking in already knowing exactly what's open with HCI.

**Weekly PM Review** — The PM weekly digest is a structured report — accomplishments, plan for next week, risks, procurement status, budget status, client communication summary — automatically generated from live data as the input for the weekly PM-to-owner update.

**The PM's Approval Authority:** PMs at HCI have authority to approve routine operational decisions within the scope of their project. AI helps the PM understand when they are approaching the threshold above which Buck's personal approval is required — flagging items that may need owner escalation before the PM has to ask.

---

## 4.3.1 Owner Command Center — Philosophy
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

**Role purpose:** Strategic oversight and final approval authority across all projects.

**What Buck needs:** A complete view of portfolio health, consolidated by risk severity and approval urgency, across all active projects simultaneously — not one at a time. He needs to know what requires his decision today and what the system is managing on its own.

**Operating model:** Buck reviews the Owner Command Center in the morning and again in the afternoon. The morning review covers new risks, pending approvals, and the day's priority actions; the afternoon check covers anything that emerged during the day. Between reviews, the system routes critical alerts to his phone via ntfy.

**Approval cadence:** Buck processes the approval queue several times per day. Items aged past their escalation threshold are flagged OVERDUE in the morning brief.

**What Buck does not want:** Status reports that require reading to extract the action. The Owner Console is designed to surface actions, not summaries. Summaries are available on request; actions are front and center.

---

## 4.3.2 Office Admin Console — Philosophy
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

**Role purpose:** Administrative coordination — incoming mail, submittal routing, permit tracking, filing, vendor communications.

**What office admin needs:** A queue-based view of items requiring administrative action: submittals to log or route, RFIs to file, permits to track, vendor certificates to collect and file.

**Operating model:** Office admin reviews the queue each morning and works through it during the day. Items are added by the system as detected — a new email matching a project, a new Drive document, a new submittal received.

**What AI does for office admin:** Reduces the "finding" work — consolidating what would otherwise mean checking email, Drive, the submittal log, and the RFI register separately into one queue, pre-sorted by urgency.

---

## 4.3.3 Accounting Console — Philosophy
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

**Role purpose:** Financial accuracy — contract tracking, invoicing, lien waivers, change order accounting.

**What accounting needs:** A project-by-project financial summary — contract value, committed costs, pending change orders, received invoices, payment status, budget variance — accurate to the dollar and updated as bids are awarded and invoices received.

**Operating model:** Accounting reviews the console weekly for routine reporting and on-demand for specific questions. The system flags when committed costs approach contract value on any project.

**What AI does for accounting:** Consolidates financial data across projects into a single view, reduces time spent pulling data for reporting, and provides audit-ready documentation of every financial decision — every bid award and change order approval logged with timestamp and approver.

---

## 4.3.4 Client Portal — Philosophy
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

**Role purpose:** Transparent client access to project status.

**What clients need:** Assurance the project is progressing — not the level of detail the PM sees. Is the project on schedule? Are there issues? What decisions do I need to make?

**Operating model:** Clients access the portal independently rather than waiting for a status call. The PM still schedules formal reviews at milestones, but the portal reduces the "quick check-in" calls that interrupt PM workflow.

**Privacy:** The client portal is scoped to project-specific information only. It never shows HCI's internal risk flags, vendor bid amounts, margin data, or anything not appropriate to share externally.

---

## 4.3.5 Trade Partner Console — Philosophy
*Authored by: Chief Architect (ChatGPT) + Browser Claude — 2026-06-30*

**Role purpose:** Vendor and subcontractor access to their own work queue with HCI.

**What trade partners need:** A clear view of their engagement with HCI — bids submitted, awards, pending submittals, open RFIs requiring their response.

**Operating model:** Trade partners self-serve status information, reducing "what's the status of my bid?" calls to the PM, while gaining visibility into their own performance metrics — which incentivizes quality vendors to maintain their standing.

**What AI does for trade partners:** Creates a direct channel between the vendor and HCI's operational data for work that involves them, without exposing data about other vendors, other projects, or HCI's internal financial position.

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

## 4.9 New BTW-5 Role Consoles — Implementation Reference (Added 2026-06-29)

### 4.9.1 Owner Command Center

**Endpoint:** `GET /gateway/role/owner`
**User:** Buck Adams (PM & Superintendent, Hendrickson Construction, Inc.; Owner, HCI-AI)

**Sections delivered:**
1. Pending approvals by priority (critical/high/normal counts + financial exposure)
2. Company financials: total contract value, total committed, commitment %, project count
3. Critical/high severity risks across ALL active projects
4. Per-project summary: health, schedule variance, open risks, committed vs contract

**Live data as of 2026-06-29:**
- $9.84M total contract value tracked across 4 active projects
- 1,039 unique pending approvals
- 1 critical risk: 101F steel delay (-5 days)

---

### 4.9.2 Office Admin Console

**Endpoint:** `GET /gateway/role/office`
**User:** Office Manager / Admin Staff

**Sections delivered:**
1. Pending approvals (action_type, description, priority, created_at)
2. Submittal queue (open submittals across all projects with due dates)
3. Overdue RFIs (past required_response_date)
4. Action summary: total items, critical count

---

### 4.9.3 Accounting Console

**Endpoint:** `GET /gateway/role/accounting`
**User:** Controller / Accountant

**Sections delivered:**
1. Company totals: total contract, total awarded, pending bids, commitment %, remaining budget
2. Per-project breakdown: contract_value, awarded, pending_bids, package counts
3. Pending financial approvals by action type

**Data sources:** `bid_entries` (awarded/pending), `bid_packages`, `projects.contract_value`, `approval_queue`

---

### 4.9.4 Client Portal

**Endpoint:** `GET /gateway/role/client/{code}`
**User:** Property owner / Client representative (read-only view)

**Sections delivered:**
1. Project health (RED/YELLOW/GREEN + schedule variance days)
2. AI summary narrative
3. Open RFIs requiring client response (with due dates)
4. Pending change orders (from approval_queue, change_order action type)
5. Recent milestones/events (awards, decisions, meetings)

---

### 4.9.5 Trade Partner Console

**Endpoint:** `GET /gateway/role/trade-partner?vendor={name}&code={project_code}`
**User:** Subcontractor / Trade Partner

**Sections delivered:**
1. Awarded bid packages for this vendor
2. All bid submissions (awarded + pending)
3. Open RFIs for the specified project
4. Action summary: awarded contracts, RFIs needing response

---

## 4.10 Complete Role Console Map (9 Consoles)

| Console | Endpoint | Role | Mobile | Auth |
|---------|----------|------|--------|------|
| Superintendent Daily | `/superintendent/{id}/today` | Field SS | ✅ | None |
| PM Weekly | `/pm/{id}/weekly` | Project Manager | 🟡 | None |
| PM Client Comms | `/mvp/projects/{code}/client-comms` | Project Manager | 🟡 | None |
| PM Action List | `/mvp/projects/{code}/action-list` | Project Manager | 🟡 | None |
| Leadership Dashboard | `/leadership/dashboard` | Leadership | ✅ | None |
| Executive Morning Brief | `/executive/morning-brief` | Executive | ✅ Push | None |
| Owner Command Center | `/gateway/role/owner` | Buck Adams | ✅ | Open |
| Office Admin | `/gateway/role/office` | Office Manager | ✅ | Open |
| Accounting | `/gateway/role/accounting` | Controller | ✅ | Open |
| Client Portal | `/gateway/role/client/{code}` | Client | ✅ | Open |
| Trade Partner | `/gateway/role/trade-partner?vendor=X` | Sub/Trade | ✅ | Open |

---

## 4.11 Cross-References

- Volume III (Project Brain) — per-project health feeding all console data
- Volume V (Executive Intelligence) — leadership escalation path
- Volume VIII (Governance) — approval gates for client/trade partner write actions
- Volume VII (Automation Architecture) — n8n workflows delivering console reports (6 daily push workflows)
- ADR-002: Per-project intelligence model
