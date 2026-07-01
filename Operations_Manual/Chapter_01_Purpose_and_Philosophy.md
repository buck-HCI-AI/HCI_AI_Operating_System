# Chapter 01 — What This System Is: Purpose & Philosophy
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 1.1 Why This System Exists

Hendrickson Construction builds luxury homes in Aspen, Colorado — one of the most demanding construction markets in the world. Projects run $3–10 million. Clients expect perfection. Schedules are tight. Mistakes are expensive. Subcontractors are scarce. Bids are complex.

Before this system, managing a project meant spreadsheets, emails, text messages, and memory. Critical information lived in Buck's head, on whiteboards, and in scattered files. Bid packages were tracked manually. Vendor relationships were undocumented. Risk was invisible until it was a problem.

The HCI AI Operating System changes that. It is a single intelligent platform that:
- Tracks every bid package across every project in real time
- Alerts the team before bids expire, budgets blow, or schedules slip
- Gives Buck a complete picture of all four live projects from any device
- Handles routine decisions automatically and escalates only what requires human authority
- Remembers everything — vendors, bids, risks, communications, history

This is not software that replaces people. It is a system that makes the team better at what they do.

---

## 1.2 The Aspen Construction Context

The Aspen luxury market operates differently from standard residential construction:

**Why bids are harder here:**
- Fewer qualified subcontractors for specialized trades (structural steel, high-end millwork, radiant systems)
- Most top subs are booked 3–6 months out — slow bid response kills timelines
- Bid validity windows are short (14–30 days) and subs won't re-bid without losing interest
- Material lead times from non-local suppliers add 6–12 weeks of risk

**Why client communication is non-negotiable:**
- Clients at this price point expect proactive, concise updates — not questions
- A surprise call from an upset client means something failed upstream
- White-glove standard: every client-facing communication is reviewed before it goes out

**Why the system matters:**
HCI runs 4 active projects simultaneously worth $15M+ in total contract value. Without an AI-assisted operations layer, managing bid expiry, schedule variance, budget tracking, and vendor relationships across all four projects simultaneously is a full-time job just for coordination. This system does that coordination automatically.

---

## 1.3 System Architecture (Plain English)

The HCI AI Operating System has four main layers:

**Layer 1 — Data**
All project data lives in a PostgreSQL database: bids, vendors, schedules, risks, budgets, daily logs. This is the single source of truth. No spreadsheet, no email, no memory — if it is not in the database, it did not happen officially.

**Layer 2 — Intelligence**
The AI team reads and analyzes data continuously:
- *GBT (Chief Architect):* Designs systems, analyzes bids, writes directives, runs strategy
- *BC (Browser Claude):* Extracts live data from Houzz, reads HubSpot, feeds intelligence into the system
- *Claude Code:* Builds and maintains the system itself — code, database, automations

**Layer 3 — Automation**
n8n workflows run on schedules:
- 7am weekday: Bid stale check → Telegram alert if anything needs attention
- 7am weekday: Schedule variance scan → flags if 101F has new overdue items
- End of day: Project health summary to Buck

**Layer 4 — Human Decision Points**
The system escalates to Buck only for:
- Contract awards and budget commitments
- Client-facing or vendor-facing sends
- Change orders and scope changes
- Hard blockers requiring login or physical action

Everything else runs autonomously.

---

## 1.4 The AI Team: Who Does What

**Buck Adams — Owner & Final Authority**
- Reviews and approves all awards, commitments, client sends
- Sets priorities and direction via Telegram (@hciaiossystem_bot) or Claude Code sessions
- Reviews the morning brief and acts on red flags
- No AI can act without Buck's authority on anything that commits HCI legally or financially

**GBT (ChatGPT — Chief Architect)**
- Designs systems and workflows
- Analyzes bid packages and recommends awards
- Writes the Operations Manual, handbooks, directives
- Runs the morning brief and project health analysis
- Communicates with Buck via Telegram

**BC (Browser Claude — Field Intelligence)**
- Extracts live data from Houzz Pro (schedules, daily logs, budgets)
- Reads HubSpot for contact and deal status
- Reports findings to GBT for analysis and to Claude Code for database loading

**Claude Code — Lead Engineer**
- Builds and maintains all code: API, database, workflows, integrations
- Executes handoffs from GBT: if GBT directs it to be built, Claude Code builds it
- Never designs — only builds what GBT directs with Buck's approval

---

## 1.5 What the System Cannot Do

These are hard limits that will never change regardless of how advanced the system becomes:

1. **Cannot award contracts.** A human must approve every subcontractor award.
2. **Cannot send client communications.** Buck reviews every client-facing message.
3. **Cannot commit to budget changes.** All budget decisions require Buck's explicit approval.
4. **Cannot hire, fire, or make employment decisions.**
5. **Cannot approve change orders.** All change orders are Buck-approved.
6. **Cannot make legal commitments on behalf of HCI.**

The AI team can recommend, prepare, analyze, and draft — but all authority to act on behalf of Hendrickson Construction remains with Buck Adams.

---

## 1.6 Design Principles

These nine principles govern every decision about what gets built and how:

1. **Does this help someone build a better project?** If not, don't build it.
2. **Human authority is non-negotiable.** AI assists; people decide.
3. **Signal over noise.** Alert on what matters. Stay quiet on everything else.
4. **Real data only.** No estimates, no assumptions in production data.
5. **The gateway is the front door.** All external access goes through the authenticated API.
6. **Build for operators, not engineers.** If a superintendent can't use it, it's not done.
7. **Automate the routine, escalate the exceptional.**
8. **One source of truth.** The database is always right. Spreadsheets are inputs only.
9. **Always advance.** Keep building. Don't stop between milestones.

---

## 1.7 Quick Start: Reading the System

**Buck — first thing every morning:**
1. Open Telegram → @hciaiossystem_bot — any alerts from overnight?
2. Check `GET /gateway/executive/mission-control` — portfolio health at a glance
3. Review approval queue — any items needing your decision today?

**GBT — session start:**
1. `GET /gateway/poll-instructions` — Buck's latest messages
2. `GET /gateway/executive/mission-control` — system state
3. `GET /gateway/project/1355R/pm` — highest-risk project first

**Claude Code — session start:**
1. Check `ls Architecture/Agent_Handoff/Inbox/` — any pending handoffs?
2. `curl https://speculate-armband-retinal.ngrok-free.dev/gateway/health` — is the gateway live?
3. Process the oldest handoff first, then continue BTW backlog

---

*This chapter is foundational. Every operator should read it before using any other part of this manual.*
*Next: Chapter 02 — Daily Operations: Morning Routine*
