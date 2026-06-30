# Volume IV — Role Intelligence
*HCI AI Construction Operating System Architecture Handbook*
**Covers: All 9 Role Consoles — Superintendent / Project Manager / Leadership / Owner / Office / Accounting / Client / Trade Partner / Executive**
**Last Updated: 2026-06-29 | Claude Code v3.5**

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

## 4.9 New BTW-5 Role Consoles — Implementation Reference (Added 2026-06-29)

### 4.9.1 Owner Command Center

**Endpoint:** `GET /gateway/role/owner`
**User:** Buck Adams (sole owner)

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
