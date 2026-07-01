# Chapter 33 — Owner & Executive Daily Workflow
**HCI AI Operations Manual | Part I — Business Operations (addendum)**
*Authority: Buck Adams | Last Updated: 2026-07-01*

> **Note on numbering:** this was originally assigned as Chapter 05 in the Chief
> Architect's chapter plan, but Chapter 05 as delivered covers Bid Package Management
> instead — this gap was identified during a system-wide manual audit and is being
> filled in as Chapter 33 rather than renumbering existing chapters. See `Operations_Manual/00_MASTER_INDEX.md`.

---

## 33.1 Overview

This chapter is about how Buck Adams runs Hendrickson Construction day to day using the AI system — not the mechanics of any one endpoint, but the actual rhythm: what arrives without being asked for, what requires a decision, and what's delegated entirely to the AI team.

The short version: the system pushes information to Buck; Buck pulls detail when something needs a decision; nothing that commits company money, awards a contract, or speaks externally on HCI's behalf happens without Buck's explicit yes.

---

## 33.2 Morning Rhythm

**07:00 — Morning Brief** arrives by email (automated, `AUTO-003`) summarizing every active project: health color, schedule status, open risks, procurement coverage. This is the first thing Buck should read — it answers "is anything on fire" before anything else.

**Throughout the day — Telegram** is the live channel. The bot (`@hciaiossystem_bot`) pushes:
- Approval requests that need a yes/no (contract awards, change orders, email sends to external parties, budget commitments) — these arrive with inline APPROVE / REJECT / HOLD buttons. Tapping one is the decision; nothing further is needed.
- Risk alerts when a project's health degrades (schedule slip, unbid procurement gap, overdue RFI blocking work).
- Status updates from whichever AI agent (Claude Code, GBT, Browser Claude) is actively working.

**`GET /gateway/role/owner`** is the on-demand company-wide view — pull this any time for: pending approvals grouped by priority with total dollar value, critical risks across every live project, and a financial summary (total contract value, total committed, commitment percentage) per project. This is the "what does the business look like right now" query.

**`GET /gateway/executive/report`** is the project-by-project morning-brief equivalent, callable any time — health, schedule variance (signed, e.g. "-5 days"), open risks, RFI status, bid coverage percentage, one-line summary per project.

---

## 33.3 What Buck Decides vs. What's Delegated

**Buck decides — no exceptions, enforced in code, not just policy:**
- Any external email send (an AI agent can draft; only Buck's Telegram approval triggers an actual send — see Chapter 24 and this system's ADR-010/011)
- Contract awards, change order approvals, budget commitments
- HubSpot writes (CRM data) — proposed, never auto-written
- Google Drive writes — dry-run logged first, then approval-gated
- Anything that creates an external commitment on HCI's behalf

**Delegated to the AI team entirely — Buck is not in this loop unless something looks wrong:**
- Drafting RFIs from plan-set review, logging them as `open` internally
- Drafting bid packages and preliminary scopes of work from plan content
- Generating a preliminary schedule (marked `draft` until a PM reviews it)
- Vendor performance tracking, historical cost lookups, market-rate research
- Monitoring schedule variance, flagging risks, escalating stale approvals
- System health monitoring, backups, restart recovery

The pattern: **anything the AI drafts, logs, or proposes internally — no approval needed. Anything that leaves the building (an email, a dollar commitment, a written contract) — Buck's yes required, every time, via Telegram.**

---

## 33.4 Weekly and Monthly Rhythm

**Monday 07:30 — Pilot Weekly Digest** (`AUTO-PILOT-WEEKLY`) — a rollup across the active pilot projects (64 Eastwood, 101 Francis, 1355 Riverside), pulled automatically.

**Friday — Executive Report review.** Same endpoint as the daily morning brief, but this is the moment to look at the week's trend, not just today's snapshot — `GET /gateway/executive/mission-control` includes `weekly_trends` (health color counts and average risk count over the last 4 weeks) for exactly this.

**Monthly — Business review.** Company-wide financials (`role/owner`'s `company_financials` block: total contract value, total committed, commitment percentage across every active project) plus a look at `role/accounting`'s pending-approval-value trend — is the approval backlog growing or shrinking month over month.

---

## 33.5 Mission Control — The Single Source of Operational Truth

`GET /gateway/executive/mission-control` is the one endpoint that answers "is the whole system, not just one project, working correctly right now":
- Portfolio health per project (reconciled against the same risk data every other view uses — see Chapter 10)
- AI team coordination state (`comms` block): pending approvals, unacknowledged directives, stale handoffs, each agent's heartbeat status (online/stale/offline), current sprint
- AI productivity (hours saved, documents processed — treat these as directional, not audited figures)
- Connector health (is HubSpot/Drive/Houzz sync current)

If Buck ever asks "is everything actually working," this is the one call that answers it — not scattered across a dozen project-specific checks.

---

## 33.6 Gate 5 and Beyond — What "Running the Company via AI" Actually Looks Like

In practice, day to day: Buck reads the morning brief, handles whatever's waiting on Telegram (usually a handful of approvals, not a flood — if it's a flood, something's wrong and worth flagging, see Chapter 25 Troubleshooting), and otherwise lets the AI team keep working. The AI team drafts, proposes, monitors, and escalates; Buck approves, rejects, or redirects. Nothing about this changes the fundamentals of running a construction company — it changes how much of the *tracking, drafting, and monitoring* labor Buck and the office team have to do personally before a decision reaches them.

**What NOT to do:**
- Do not treat an AI-drafted RFI, bid package, or schedule as final without review — they're explicitly marked (`open`/`not_started`/`draft`) precisely so this distinction stays visible.
- Do not approve a Telegram request without reading what it actually says — the buttons make approving fast, not mindless.
- Do not assume silence means nothing needs attention — check the morning brief and Mission Control daily; the system pushes what it can, but a stale AI-agent heartbeat or a growing approval backlog is something to notice, not wait to be told about.

---

*This is an addendum to Part I — Business Operations. See Chapter 24 (Approval Queue & Notification System) for the technical mechanics behind the approval flow described here, and Chapter 18 (Daily System Monitoring) for the AI-system-health side of Mission Control.*
