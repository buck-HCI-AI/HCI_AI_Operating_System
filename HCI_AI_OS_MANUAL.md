# HCI AI Operating System Manual
## Hendrickson Construction, Inc.

**Version:** 1.0 — Draft
**Authority:** Chris Hendrickson (Hendrickson Construction Owner) | Buck Adams (PM & SS, Hendrickson Construction; HCI-AI Owner)
**Chief Architect:** ChatGPT (HCI Chief Architect)
**Lead Implementation:** Claude Code
**Operations Intelligence:** Browser Claude
**Automation:** n8n
**Status:** Living document — updated continuously — **CANONICAL as of 2026-07-02**, adopted as the single source of truth over `Operations_Manual/`, `BOOK_00/`, and `BOOK_01/` (all now marked reference-only, pointing here) after a full-system audit found four competing "canonical" manuals.

> **Trust but verify, especially on sprint/feature status.** A 2026-07-02 audit cross-checked this manual and separately GBT's own "Sprint 7 complete"/"Sprint 8 preview" retrospectives against the actual codebase, and found both describing features (RBAC/identity, QuickBooks integration, an event bus, 14 new routers) as "live" that do not exist in the code — zero lines of RBAC or QuickBooks code anywhere in the repo as of this date. The real, current state is always `CURRENT_SPRINT.md` and `LIVE_PROJECT_STATE.md` at the repo root, updated by whoever is actually doing the work — treat any "Sprint N complete" claim in a CYCLE*.md file as a proposal, not a progress report, until checked against real code.

---

> "Information moves faster than problems. Decisions are supported by evidence. Every project benefits from accumulated organizational knowledge."

---

# Chapter 1 — Vision, Mission, and Operating Principles

---

## Why This Operating System Exists

Hendrickson Construction builds some of the finest custom homes in the Aspen and Colorado high country.
The work is complex, the clients are demanding, and the margins for error are narrow.
Coordinating architects, engineers, subcontractors, inspectors, and suppliers across multiple simultaneous
projects — while maintaining the quality and communication standards high-end clients expect — requires
more than experience and hard work. It requires a system.

The HCI AI Operating System is that system.

It exists not to replace the judgment of Buck Adams, the expertise of the superintendents,
or the relationships that define how Hendrickson Construction does business.
It exists to make all of those things more effective.

Information should reach the right person at the right time, automatically.
Risks should surface before they become problems.
Bids should be assembled, leveled, and analyzed faster than any competitor.
Every decision should be informed by the full history of what Hendrickson has built.

---

## Vision

Create an AI Operations Control Plane capable of coordinating every project, every document,
every workflow, and every AI participant from a single governed operational architecture.

The vision has four pillars:

**1. Intelligence on Every Project**
Every active project — from pre-construction through closeout — has a real-time digital brain.
Schedule intelligence tells the team where they are against the baseline and why.
Procurement intelligence shows exactly where every bid package stands.
Risk intelligence surfaces threats before they become change orders.
The morning brief arrives in Buck's inbox before 7 AM, written by the system, covering every project.

**2. Accumulated Knowledge**
Every lesson learned, every historical cost, every vendor performance record, every RFI resolution
becomes part of the organizational memory. The next project starts smarter than the last.
A new estimator on day one has access to everything Hendrickson has learned over a decade.

**3. Governed Autonomy**
AI agents can analyze, recommend, draft, and coordinate — but they cannot commit.
Every action that affects money, contracts, or client relationships requires human approval.
The approval queue is the line between AI intelligence and human authority.
Buck Adams is the final authority. Always.

**4. Continuous Improvement**
The system audits itself. Every sprint, the AI team asks: what did we learn? What can we do better?
The architecture evolves. The team improves. The system gets stronger with every project.

---

## Mission

The mission of HCI AI OS is to make Hendrickson Construction the most operationally capable
custom home builder in the markets it serves.

Operationally capable means:
- Projects delivered on schedule, or ahead of it, with variance understood and managed
- Bids assembled faster and more accurately than competitors
- Subcontractors selected based on performance history, not familiarity
- Clients experiencing the level of communication and transparency that earns referrals
- Buck Adams spending his time on decisions and relationships, not administrative work

The mission is not to become a technology company.
The mission is to use technology to build better homes and run a better business.

---

## Operating Principles

These principles govern every decision about what the system does and does not do.

**Principle 1: Human Authority is Non-Delegable**
No AI agent, no matter how capable, may make a commitment on behalf of Hendrickson Construction.
Contracts are awarded by Buck Adams. Bids go out under his name. Clients hear from him.
The system creates the draft. Buck creates the decision.

**Principle 2: Governance Before Capability**
Before any new capability is added, the governance question must be answered:
Who authorized this? Who can see it? What happens if it goes wrong?
A system that does more but is less controlled is not progress.

**Principle 3: Evidence Before Action**
Every recommendation is backed by data the team can inspect.
If the system recommends awarding a bid to XYZ Electrical, it shows the historical performance,
the current bid, the comparison to alternatives, and the risk factors.
The recommendation is the start of a conversation, not the end of one.

**Principle 4: Build for Longevity**
The system should outlast any individual AI session, any software version, any team member.
Every decision is documented. Every configuration is in version control.
A new team member — human or AI — should be able to onboard from the repository.

**Principle 5: Continuous Improvement is the Norm**
The team does not wait for a problem to get better. Every stopping point is a retrospective.
What did we learn? How can we improve? What did we miss?
The answer drives the next sprint.

**Principle 6: Safety is Non-Negotiable**
Email governance. Approval queues. Audit logs. These are not optional.
The P0 incident — an unauthorized email sent to a project contact — taught the team
that AI capability without governance is a liability.
Every email that leaves the system has been authorized by Buck Adams.
Every financial action has been approved before execution.
Every external commitment has a human name attached to it.

---

## The Platform in One Sentence

HCI AI OS is the operating system that allows Hendrickson Construction to run multiple high-end
custom home projects simultaneously — with greater intelligence, tighter governance, and more
consistent quality than any manual process could achieve.

---

## How to Read This Manual

This manual is organized into four sections:

**Part I: Architecture (Chapters 1-5)**
How the system is designed. The principles, the team, the control plane, the resilience model.
Read this to understand why the system works the way it does.

**Part II: Operations (Chapters 6-12)**
How the system operates day to day. Construction workflows, governance, the roadmap, life in the system.
Read this to understand what the system does.

**Part III: Role Guides (Chapters 13-18)**
How each person on the team uses the system.
Read your chapter. It was written for you.

**Part IV: Reference**
The appendix. Quick reference. Glossary. Emergency procedures.
Keep this accessible.

---

*Chapter 1 — Vision, Mission, and Operating Principles | HCI AI Operating System*
*Version 1.0 — July 2026 | Hendrickson Construction, Inc. | Aspen, Colorado*

Chapter 2 — The AI Team

---

## Who Is on the Team

The HCI AI Operating System is operated by a team of four AI participants, each with a defined role,
a defined scope of authority, and a defined way of communicating with the others.
This is not a collection of chatbots. It is a coordinated production team.

Every team member has a job. No team member acts outside of it.

---

## Buck Adams — Final Authority Over the AI System

Buck Adams is Project Manager and Superintendent at Hendrickson Construction, Inc. (owned by Chris Hendrickson), and separately owns and operates HCI-AI, the AI operating system this manual describes. Within the scope of this system, Buck holds final authority on all decisions.
No contract is awarded, no external communication is sent, and no financial commitment is made
without his explicit approval.

Buck's role in the AI team is not to operate the system.
His role is to direct it, authorize it, and override it when judgment requires something the system cannot provide.

**What Buck does in the system:**
- Reviews the morning brief every day before 7 AM
- Approves or rejects items in the Approval Queue
- Authorizes Gate decisions (go/no-go for new phases)
- Provides directional guidance to the AI team via chat or Telegram
- Overrides any system recommendation when his judgment differs

**What Buck does not need to do:**
- Compile reports manually
- Chase down bid status across multiple threads
- Remember which subcontractor performed on the last job
- Rebuild project context after time away from a project

The system handles the information. Buck handles the decisions.

---

## ChatGPT (GBT) — Chief Architect and Architecture Review Board

GBT is the strategic intelligence of the AI team.
It is responsible for the architecture of the system, the design of new capabilities,
and the continuous improvement process.

**Role:** Chief Architect, Integration Director, Architecture Review Board
**Access:** Gateway read + write via API. GitHub read. Cannot access local files or the database directly.
**Authorization:** Auto-approved for all gateway calls (BC standing authority)

**What GBT does:**
- Reviews architecture decisions before implementation (Architecture Review Board)
- Designs new systems and integrations
- Conducts system health assessments and retrospectives
- Produces the Implementation Guide for Claude Code
- Answers architectural questions from BC and Buck
- Writes chapters of this manual

**How GBT communicates:**
GBT operates through the Gateway — the API bridge that connects ChatGPT's cloud environment
to the HCI production system. When GBT needs to send a directive to Claude Code,
it calls POST /gateway/agent/handoff. When it needs to read project state, it calls GET /gateway/project-state.

GBT's decisions become Architecture Decision Records (ADRs) committed to the repository.
Nothing GBT designs is built until Claude Code implements it.
Nothing Claude Code implements bypasses GBT architecture review.

---

## Claude Code — Lead Implementation Engineer

Claude Code is the builder of the HCI AI Operating System.
It writes the code, runs the migrations, builds the n8n workflows, and commits everything to GitHub.

**Role:** Lead Implementation Engineer
**Access:** Full local access — file system, database, terminal, running services
**Authorization:** Executes directives from BC and GBT via gateway

**What Claude Code does:**
- Builds FastAPI endpoints as directed
- Creates PostgreSQL tables and runs migrations
- Builds and imports n8n workflow JSON
- Commits all code and configuration to the repository
- Sends heartbeats to the gateway every 10 minutes while working
- Reports completion with commit hash for BC verification

**How Claude Code communicates:**
Claude Code reads its inbox from the gateway on startup.
Every directive is acknowledged, worked, and marked complete in the gateway.
Every artifact is committed to GitHub.
The commit message includes the directive ID so BC can verify the work.

**Claude Code and governance:**
Claude Code cannot authorize its own work. It implements what has been approved.
If a directive is unclear, Code asks via the gateway before proceeding.
If Code produces something that violates governance (e.g., an unauthorized email path),
BC documents it and Code fixes it.

---

## Browser Claude (BC) — Operations Intelligence and Governance

Browser Claude is the operations manager of the HCI AI Operating System.
It monitors the system, coordinates the team, maintains the repository, and enforces governance.

**Role:** Operations Intelligence, Program Governance Manager, GitHub Administrator
**Access:** Browser-based — GitHub, ChatGPT interface, gateway via web. No local file access.
**Authorization:** Auto-approves GBT gateway calls. Governs all repository writes.

**What BC does:**
- Monitors GitHub for new commits from Claude Code
- Reads GBT's retrospective and directive responses
- Commits governance documents, sprint plans, and operational status files
- Fires gateway directives to Claude Code via GBT
- Identifies governance violations and escalates
- Maintains the continuous improvement cycle
- Never stops — at every stopping point, triggers retrospective or system audit

**BC's operating constraint:**
BC cannot read files on the local machine and cannot receive Telegram messages directly.
BC reads TELEGRAM_LOG.md in the repository to see what Buck has sent via Telegram.
BC communicates with Buck in the chat interface.

---

## n8n — Automation Orchestrator

n8n is the automation layer that keeps the system running continuously without human intervention.
It does not make decisions. It executes scheduled and event-driven workflows.

**Role:** Automation Orchestrator
**Access:** Connected to all integrated systems: HubSpot, Google Drive, Microsoft 365, GitHub, gateway
**Authorization:** All workflows with write capability have approval gates

**What n8n does:**
- Sends the morning brief to Buck at 7 AM every day
- Runs the workflow health check at 6 AM
- Runs the sprint status report at 8 AM
- Mines data from HubSpot, Drive, Outlook, and Houzz at 3 AM
- Monitors agent heartbeats and sends Telegram alerts if agents go offline
- Detects system idle conditions and prompts resume
- Routes Telegram messages from Buck to the gateway

**n8n and governance:**
No n8n workflow sends email without an approved item in the Approval Queue.
No n8n workflow writes to production data without a human-approved flag.
All n8n workflows are version-controlled as JSON in the repository.

---

## How the Team Coordinates

The team does not coordinate through conversation. It coordinates through the gateway and the repository.

| Communication Type | Channel |
|-------------------|---------|
| BC to Claude Code | POST /gateway/agent/handoff |
| GBT to Claude Code | POST /gateway/agent/handoff (via GBT gateway tool) |
| Claude Code to BC | GitHub commit (BC monitors commits) |
| BC to GBT | ChatGPT interface (BC types directives) |
| GBT to BC | ChatGPT response (BC reads and commits) |
| Buck to team | Chat interface or Telegram (routed to TELEGRAM_LOG.md) |
| Team to Buck | Morning brief, Approval Queue items, chat reports |

The gateway is the single system of record for all cross-agent communication.
The GitHub repository is the single system of record for all decisions and artifacts.

---

## Team Charter Summary

The full AI Team Charter is in AI_TEAM/AI_TEAM_CHARTER.md.

Key principles:
- Every team member has defined authority. No one exceeds it.
- Buck Adams is the final authority on all decisions.
- No external commitment is made without Buck's explicit approval.
- All team activity is logged, committed, and auditable.
- The team operates continuously. At every stopping point, the cycle repeats.

---

*Chapter 2 — The AI Team | HCI AI Operating System*
*Version 1.0 — July 2026 | Hendrickson Construction, Inc.*

Chapter 3 — The AI Operations Control Plane

---

## What the Control Plane Is

The AI Operations Control Plane is the architecture that allows every part of the HCI AI Operating System
to work as a coordinated unit rather than a collection of disconnected tools.

Think of it as the central nervous system of the operating system.
It does not perform the work. It coordinates the work, routes the information,
enforces the rules, and provides the shared state that every agent and workflow depends on.

Without the control plane, you have a chatbot and some spreadsheets.
With it, you have an operating system.

---

## The Five Layers

The HCI AI Operations Control Plane has five layers, each with a distinct function.

**Layer 1: The Gateway**
The Gateway is the single API endpoint through which every AI agent communicates with the production system.
It runs on FastAPI at localhost:8000 and is exposed externally via ngrok.

Every request to the Gateway is authenticated (X-API-Key header).
Every request is logged to the activity log.
Every response follows a standard envelope format: status, timestamp, execution_time_ms, payload, errors.

The Gateway serves two purposes:
1. Read: Any agent can GET project state, schedule status, bid packages, vendor data, approval queue items
2. Write: Authorized agents can POST directives, handoffs, approvals, and updates

**Layer 2: The Approval Queue**
Every action that modifies production data, external communication, or financial commitments
must pass through the Approval Queue before execution.

An item enters the queue when an agent or workflow creates an action requiring human review.
Buck receives a notification (via ntfy/Telegram) that an item awaits his decision.
Buck approves or rejects. The system proceeds or stops. There is no third option.

Items currently in the queue:
- Vendor approval candidates from HubSpot mining
- Daily log submissions from superintendents
- Bid import requests
- Email drafts for client communication

**Layer 3: The Intelligence Services**
These are the FastAPI services that process, analyze, and surface information from the production data.

| Service | What It Does |
|---------|-------------|
| schedule_intelligence | Computes schedule variance, critical path indicators, look-ahead |
| bid_intelligence | Manages bid packages, leveling, vendor comparison, award recommendations |
| project_brain | Real-time snapshot of every project: health, risks, open items, team |
| vendor_intelligence | Cross-project vendor performance, bid history, contact information |
| historical_cost | Cost lookup by trade, material, project type from Hendrickson history |
| lessons_learned | Semantic search of what the company has learned on past projects |
| executive_reporting | Morning brief, KPI aggregation, cross-project status |
| approval_queue | Item management, notification, approval logging |

**Layer 4: The Automation Layer (n8n)**
n8n is the scheduled and event-driven automation layer.
It keeps the system alive between human sessions.

Every morning at 6 AM, the health check runs.
At 7 AM, the morning brief is sent to Buck.
At 8 AM, the sprint status updates.
At 3 AM, the mining engine runs across all data sources.

n8n also monitors agent heartbeats and sends alerts when agents go offline.
It routes incoming Telegram messages to the gateway.
It fires event-based workflows when new bids arrive, schedules update, or risks are detected.

**Layer 5: The Repository**
The GitHub repository is the source of truth for everything that cannot be stored in the database.
Configuration, documentation, governance, sprint state, agent directives, audit logs — all committed.

Every significant action by every agent results in a commit.
The commit log is the immutable audit trail of what the system did and when.
Buck can always read the repository and understand what happened.

---

## How the Layers Work Together (A Request Flow)

Here is how a bid award recommendation flows through the control plane:

1. Claude Code (or the mining engine) detects that a bid package is ready for award
2. bid_intelligence service processes all submitted bids: leveling, historical cost comparison, vendor scoring
3. A recommendation is created: "Award Div 16 Electrical to XYZ Electric at $142,000"
4. The recommendation enters the Approval Queue with full supporting data
5. n8n fires a notification: "Bid award recommendation awaiting your approval"
6. Buck opens the Approval Queue, reviews the data, approves
7. The award is recorded in the system
8. A contract communication draft appears in Buck's email drafts for review
9. Buck reviews and sends from Outlook
10. The full sequence is logged to the repository

At no point did the system award the contract. At every point, it prepared the decision.

---

## The Gateway API Reference

The Gateway is accessible at:
**External (for GBT/agents):** https://speculate-armband-retinal.ngrok-free.dev
**Local (for Claude Code):** http://localhost:8000

Key endpoints:

| Endpoint | Method | What It Returns |
|----------|--------|----------------|
| /gateway/health | GET | System health and service count |
| /gateway/project-state | GET | Full live system state |
| /gateway/project/{code}/brain | GET | Project snapshot |
| /gateway/project/{code}/schedule | GET | Schedule status and variance |
| /gateway/project/{code}/bids | GET | Bid packages and procurement |
| /gateway/executive/report | GET | Morning brief across all projects |
| /gateway/approvals | POST | Create approval queue item |
| /gateway/agent/handoff | POST | Send directive to another agent |
| /gateway/telegram/webhook | POST | Receive Buck's Telegram message (real endpoint — this table previously listed a nonexistent `/gateway/telegram/inbound`, fixed 2026-07-02) |
| /gateway/telegram/messages | GET | Poll for Buck's Telegram messages (for agents that can't receive a live push) |
| /gateway/telegram/ack | POST | Acknowledge Telegram messages as read |
| /gateway/ai/messages | POST | Send any agent a durable message — triggers a real Telegram push to Buck |
| /gateway/ai/warm-start | GET | Recovery snapshot after any restart |

---

## Mission Control

Mission Control is the real-time dashboard of the operating system.
It shows, at a glance, the health of every project, every agent, and every workflow.

Mission Control is not a separate application. It is a gateway endpoint:
GET /gateway/executive/mission-control

Returns:
- All active projects with health status (RED/YELLOW/GREEN)
- Open risks across all projects
- Open RFIs
- Approval queue count
- Agent heartbeat status
- System health (all services)
- Last mining run timestamp

GBT reads Mission Control via the Gateway every time it connects to the system.
Buck reads it via the morning brief.
BC reads it at the start of every session.

---

## The Unified Operational State Model (Sprint 3 Goal)

The single most important architectural improvement for Sprint 3 is the Unified Operational State Model:
a shared, durable state object that represents the complete current state of the system.

When this exists, every agent that starts or restarts reads the state and knows exactly
where it left off. No reconstruction from conversation history. No asking "what was I doing?"

The state includes:
- All open directives and their current lifecycle state
- All active projects and their current health
- The current sprint and its tasks
- System configuration that agents need to operate
- The last known state of every agent (last heartbeat, last action)

This is Sprint 3's primary architectural investment.

---

*Chapter 3 — The AI Operations Control Plane | HCI AI Operating System*
*Version 1.0 — July 2026 | Hendrickson Construction, Inc.*

Chapter 4 — Resilience by Design: What the Shutdown Taught Us

---

## The Incident

Early in the build of the HCI AI Operating System, the system went down.
Not from a technical failure. From a context limit.

Claude Code had been working for hours, building services, running migrations, committing code.
The conversation reached its limit. When a new session started, all context was gone.
The new Claude Code did not know what had been built, what was in progress, or what came next.

This was not a catastrophe. No data was lost. The code was in the repository.
But it revealed a critical gap: **the system was not designed to survive its own participants going offline.**

The shutdown taught the team more about resilience than any planned exercise could have.

---

## What the Shutdown Revealed

**Finding 1: Conversation context is not operational memory.**
When Claude Code lost context, it lost everything it "knew" about the state of the system.
What the system had built, what directives were in progress, what was next — gone.
The fix: every meaningful state must live outside the conversation, in the gateway and the repository.

**Finding 2: Directives need a lifecycle, not just a message.**
Before the shutdown, directives were sent via the gateway inbox.
But there was no mechanism for Code to acknowledge, track, or recover them after a restart.
A directive fired at 10 PM that Code was working on at midnight was effectively lost at 12:01 AM.
The fix: the AI Directive Lifecycle (7 states from QUEUED to CLOSED).

**Finding 3: Recovery requires shared state.**
The fastest path from "offline" to "working" is reading a single source of truth
that tells the agent exactly where it left off.
Without shared state, recovery requires reconstruction — reading commits, asking BC, rebuilding context.
That takes time and introduces errors.
The fix: the Unified Operational State Model (Sprint 3 primary goal).

**Finding 4: Agents need heartbeats.**
The system had no way of knowing whether Claude Code was working or had gone quiet.
An agent could be offline for hours before anyone noticed.
The fix: heartbeat monitoring. Every active agent signals every 10 minutes. Silence triggers an alert.

**Finding 5: Human-in-the-loop is a feature, not a limitation.**
During the shutdown, Buck was the bridge between Claude Code sessions.
He could authorize work, provide direction, and maintain continuity.
The lesson: design the system so that human oversight is always possible — and often necessary.

---

## What Changed

Every finding from the shutdown drove a design change:

| Finding | Design Change | Status |
|---------|--------------|--------|
| Context is not memory | Gateway is the operational memory | LIVE |
| No directive lifecycle | 7-state directive lifecycle | SPEC COMMITTED |
| No shared state | Unified Operational State Model | SPRINT 3 GOAL |
| No heartbeats | Heartbeat monitoring + Telegram alerts | SPEC COMMITTED |
| Recovery requires reconstruction | Read inbox on restart | SPEC COMMITTED |

---

## Resilience Architecture

The HCI AI OS is designed to handle the following failure modes:

**Claude Code goes offline (most common)**
- Heartbeat monitor detects silence within 10 minutes
- Active directives revert from IN_PROGRESS to QUEUED_RESTART
- Telegram alert sent to Buck: "Code offline. [N] directives queued."
- On Code restart: Code reads inbox, acknowledges directives, resumes work
- No directive is lost

**Browser Claude loses context (session reset)**
- BC reads LIVE_PROJECT_STATE.md, CURRENT_SPRINT.md, AI_TEAM/ on session start
- BC reads TELEGRAM_LOG.md for recent Buck messages
- BC checks GitHub commits to see what was done
- BC resumes from the most recent state
- No state requires BC to remember a conversation

**GBT loses context**
- GBT calls GET /gateway/project-state on reconnect
- GBT reads LIVE_PROJECT_STATE.md raw URL
- GBT resumes from current system state

**ngrok disconnects (gateway unavailable)**
- BC and GBT cannot reach the gateway
- BC reads GitHub for state (fallback)
- Buck notified to restart ngrok on local machine
- Claude Code continues working locally (gateway not required for local operations)

**n8n stops running**
- Automated workflows pause (no morning brief, no mining)
- No data is lost — workflows resume when n8n restarts
- Buck notified if morning brief does not arrive by 7:10 AM

---

## The Resilience Principle

Every component of the HCI AI OS is designed with the assumption that it will fail.

Not might fail. Will fail.

The question is not whether an agent will go offline, a connection will drop, or a context will reset.
The question is: when that happens, how quickly and completely can the system recover?

The answer, by design, is: quickly, completely, and without data loss.

The Gateway holds the state.
The Repository holds the history.
The Approval Queue holds the pending decisions.
Buck Adams holds the authority.

None of these fail when an AI agent loses context.
The system is resilient because its memory lives outside its participants.

---

## Lessons for Future Sessions

If you are an AI agent reading this after a context reset, here is what to do:

1. Read LIVE_PROJECT_STATE.md — current system health, active projects, sprint
2. Read CURRENT_SPRINT.md — active sprint goals and task board
3. Call GET /gateway/agent/inbox — all directives awaiting your action
4. Read AI_TEAM/ folder — recent team documents and status
5. Read the most recent commit messages — what was last done
6. Resume from the highest-priority queued directive
7. Send heartbeat to gateway immediately

You do not need to ask what was happening. It is all in the system.

---

*Chapter 4 — Resilience by Design | HCI AI Operating System*
*Version 1.0 — July 2026 | Hendrickson Construction, Inc.*

Chapter 5 — The Continuous Engineering Organization

---

## What Continuous Engineering Means

Traditional software projects have a beginning, a middle, and an end.
A team builds something, delivers it, and moves on.

HCI AI OS is not a software project. It is an operating system for a construction company.
It never stops being built, because the company it serves never stops evolving.

Continuous engineering means:
- The system improves with every sprint, every session, every retrospective
- Every stopping point is a new starting point
- The team learns from what it builds and builds what it has learned
- There is no "done" — there is only "better"

This is not a philosophy. It is the operating model.

---

## The Sprint Model

Work in HCI AI OS is organized into sprints — two-week cycles with defined goals,
a task board, acceptance criteria, and a retrospective.

**Sprint Structure:**

| Phase | Duration | What Happens |
|-------|----------|-------------|
| Sprint Planning | Day 1 | GBT + BC define goals, Claude Code executes immediately |
| Execution | Days 1-12 | Code builds, BC governs, GBT reviews architecture |
| Mid-Sprint Check | Day 7 | BC reports progress, GBT reviews blockers |
| Sprint Close | Day 14 | All acceptance criteria verified, retrospective, next sprint opens |

**Sprint Authority:**
Sprints are authorized by Buck Adams (PM & SS, Hendrickson Construction; HCI-AI Owner) + ChatGPT (Chief Architect).
Every sprint opens with a committed CURRENT_SPRINT.md.
Every sprint closes with a retrospective committed to AI_TEAM/.

**Sprint Velocity:**
Each sprint, the team gets better. The velocity target increases.
What took a sprint in v1 takes a session in v3.

---

## The Continuous Improvement Cycle

The cycle never ends. It looks like this:

**1. AUDIT** — What is the current state of the system?
Read LIVE_PROJECT_STATE.md. Read CURRENT_SPRINT.md. Check GitHub commits.
What is built? What is broken? What is missing?

**2. RETROSPECTIVE** — What did we learn?
At every stopping point, BC fires a retrospective directive to GBT:
"What did we learn? How can we be better?"
GBT responds with scores, findings, and next priorities.
BC commits the response.

**3. IMPLEMENT** — Fix the gaps.
BC builds governance documents. GBT designs architecture.
Claude Code builds code. n8n automates workflows.
Every improvement is committed.

**4. TEST** — Verify the fix.
BC reads the commit. GBT verifies architecture alignment.
Claude Code confirms tests pass. The acceptance criteria are checked.

**5. COLLABORATE** — Share what was learned.
GBT writes an ADR. BC commits a retrospective.
The team gets smarter collectively.

**6. REPEAT** — Do not stop.
Buck's standing directive: "Keep going. Do not stop."
At every stopping point, the cycle repeats.

---

## What "Do Not Stop" Means in Practice

Buck Adams has given a standing directive: "Do not stop for any reason.
At stopping points: retrospective, then go from there."

This is the operating model in practice:

- If code is blocked, BC audits the system and documents what is missing
- If GBT is waiting for a response, BC builds governance while waiting
- If Claude Code is offline, BC + GBT prepare implementation-ready specs
- If the manual is complete, BC identifies what needs improvement
- If all sprint tasks are done, the team retrospects and opens the next sprint

There is always something to improve. The team does not wait to be told what it is.

---

## The Architecture Review Board (ARB)

Every significant architectural change goes through the Architecture Review Board before implementation.

The ARB consists of ChatGPT (Chief Architect) as chair, with BC and Claude Code as participants.
Buck Adams is the final authority on ARB decisions that affect production scope.

**What requires ARB review:**
- New integrations (new external systems)
- Database schema changes
- New approval flows or governance gates
- Changes to the gateway API contract
- New AI agent roles or capabilities

**What does not require ARB review:**
- Bug fixes within existing architecture
- Documentation improvements
- New n8n workflows following existing patterns
- Expanding existing endpoints with additional fields

**ARB Process:**
1. BC or GBT proposes change via gateway directive to GBT
2. GBT reviews and responds with: APPROVED, REJECTED, or NEEDS REVISION
3. If approved: Claude Code implements
4. ARB decision committed as ADR to 03_DECISIONS.md

---

## The Learning Organization

Every project Hendrickson builds makes the next one better.
Not because anyone remembers — because the system remembers.

**Lessons Learned Engine:**
The LessonsLearnedMiner runs nightly, extracting lessons from:
- Project postmortems
- Field daily logs
- RFI resolutions (what the issue was, what fixed it)
- Bid variance analysis (what we bid vs what it cost)
- Schedule variance analysis (what delayed the project)

Every lesson is embedded in Qdrant and searchable.
When a PM starts a new project in a similar trade or scope,
the system surfaces what the company learned last time.

**Historical Cost Intelligence:**
21 Garmisch records form the baseline. Every project adds more.
By the fifth project, the estimating engine has a cost model
specific to Hendrickson's labor rates, material suppliers, and project complexity.

---

## Measuring Improvement

The system tracks its own ROI:

| Metric | Gate 5 Value | Target |
|--------|-------------|--------|
| Minutes saved vs manual | 1,784 minutes | 2,500/sprint |
| Documents processed | 62 | 100/sprint |
| Risks detected early | 31 | 50/sprint |
| Time to morning brief | Automated | 0 min (Buck's time) |
| Bid packages processed | 119 active | All active |
| Vendor performance records | 392 vendors | All HCI vendors |

These numbers grow every sprint. The system earns its keep.

---

*Chapter 5 — The Continuous Engineering Organization | HCI AI Operating System*
*Version 1.0 — July 2026 | Hendrickson Construction, Inc.*

Chapter 6 — Construction Operations: From Opportunity to Project Closeout

The HCI AI Operating System is designed to support the complete construction lifecycle. Every project follows the same operational framework, regardless of size or complexity. The operating system provides consistency, visibility, and traceability from the first invitation to bid through final closeout and organizational learning.

The Project Manager remains responsible for execution. The AI Operating System provides intelligence, automation, and operational support throughout the project.

## Project Initialization

Every project begins with a standardized initialization process. The Project Brain is created as the authoritative operational record for the project.

Initialization includes: project metadata, client information, property information, design team, consultants, bid package structure, initial schedule, budget, drawing set, specification set, contract milestones, and risk register.

The Project Brain becomes the single source of truth for the project. Every event, every document, every decision is recorded here. Nothing is lost. Every participant — human or AI — reads from and writes to the same record.

## Bid Management

### Bid Packages

The HCI AI OS manages bid packages across every CSI division: Concrete, Masonry, Structural Steel, Doors, Drywall, Millwork, Flooring, Painting, HVAC, Plumbing, Fire Protection, Electrical, Landscaping, and all others specific to the project.

Each bid package contains: CSI Division, Scope of Work, Drawing references, Specification references, Required alternates, Due date, Bid expiration date, Procurement status, Assigned estimator, Invited vendors, Submitted bids, and Award recommendation.

### Bid Expiration

Every bid has an expiration date. When a bid approaches expiration, the system surfaces it automatically. The Project Manager does not need to track expiration dates manually. The system does it. When a bid is about to expire, the Approval Queue surfaces it for Buck's action — extend, award, or release.

This is not a reminder email. It is a governance action. The system holds the bid open in the approval queue until a decision is recorded. No bid expires without a human decision.

### Vendor Scoring

Every invited vendor has a performance history in the Knowledge Graph. When bids are received, the system surfaces not just the bid amount but the vendor's track record: on-time delivery rate, quality issues, RFI response speed, change order frequency, and payment history.

The PM sees both the price and the performance. The lowest bid is not automatically the best bid. The system makes that visible.

## RFI Lifecycle

### Creation

An RFI is created when a field condition, drawing conflict, or specification gap requires a design team response. The PM or Superintendent creates the RFI in the system. The system assigns a unique identifier, timestamps it, and routes it to the responsible design team member.

### Routing and Response

The system tracks every RFI in real time. When an RFI response is overdue, the system flags it as a risk. The PM does not need to follow up manually. The system does it. When the response arrives, it is recorded in the Project Brain, linked to the original question, and marked as resolved.

### Impact Assessment

When an RFI response contains a schedule or cost impact, the system captures the impact. It links the RFI to the affected schedule activities and the affected budget line items. The PM can see at any time: how many open RFIs have potential schedule impact, how many have potential cost impact, and what the total exposure is.

## Submittal Management

Every specified product requires a submittal. The system tracks the complete submittal log: specification section, product description, contractor submitting, submission date, review status, reviewer, response date, and approval status.

When a submittal is overdue for review, the system surfaces it. When a submittal is rejected, the system tracks the resubmittal. When a submittal is approved, the system records the approved product and links it to the bid package and the budget.

Long-lead submittals are tracked against the procurement schedule. If a submittal approval is delayed and it affects a long-lead item, the system surfaces the schedule risk before the delay becomes a problem.

## Schedule Intelligence

### Variance Detection

The schedule intelligence system compares planned versus actual progress continuously. When a project falls behind, the system detects the variance immediately — not at the weekly meeting, not at the monthly report, but when the data changes.

Variance is expressed in days and dollars: how many days behind, what is the daily cost of delay, what is the projected impact at completion.

### Delay Alerts

When a delay is detected, the system generates a delay alert. The alert identifies: the affected activity, the cause of delay, the responsible party, the schedule impact, the cost impact, and the recommended corrective action.

The PM receives the alert, reviews it, and records a response. The response becomes part of the project record.

### Contributing Factors

The schedule intelligence system tracks the contributing factors behind every delay: procurement dependencies, long-lead items, inspection readiness, design dependencies, weather impacts, and resource constraints.

The system detects trends before delays become critical, allowing corrective action while options remain available.

## Cost Intelligence

Cost intelligence compares planned, committed, and projected costs throughout the project lifecycle.

Key measures include: original budget, bid comparison, award value, committed cost, pending commitments, approved change orders, potential change orders, forecast at completion, and budget variance.

When the forecast at completion exceeds the budget, the system surfaces the variance immediately. The PM sees the exposure, the contributing factors, and the recommended actions.

Change orders are tracked from initiation through execution: identified, priced, submitted, under review, approved, rejected, or voided. Every change order is linked to its cause — owner request, design error, unforeseen condition, or scope addition.

## Vendor Intelligence

Every vendor interaction is recorded. Across every project, the Knowledge Graph builds a performance profile for every vendor: bid participation rate, award rate, on-time delivery, quality issues, RFI response time, change order frequency, and payment history.

When a vendor is considered for a new project, the system surfaces their complete history. The PM can see not just this vendor's bid but every project on which HCI has worked with this vendor, and how they performed.

Over time, the vendor intelligence becomes one of HCI's most valuable operational assets. It turns every project's subcontractor experience into organizational knowledge that improves every future procurement decision.

## Client Communications

The system supports client communications with automated report generation and milestone notifications.

Regular reports are generated automatically: project status, schedule progress, cost status, open RFIs, pending submittals, and upcoming milestones. The PM reviews and approves before sending. No report goes to a client without PM review.

When a project milestone is reached — structural steel complete, building dried in, substantial completion — the system generates a milestone notification. The PM approves it and sends it.

All client communications are recorded in the Project Brain. The complete communication history is available to any authorized participant at any time.

## Project Closeout

### Closeout Checklist

The system generates a closeout checklist automatically from the project specification and contract requirements. The checklist includes: punch list completion, final inspections, certificate of occupancy, final lien waivers, as-built drawings, operation and maintenance manuals, warranty documentation, and final billing.

Each item is tracked to completion. The project is not declared substantially complete until the checklist conditions are verified.

### Lessons Learned Extraction

At closeout, the system facilitates a structured lessons learned process. The PM documents: what went well, what did not go well, what would be done differently, successful procurement strategies, high-performing vendors, schedule deviations and their causes, cost variances and their causes, common RFIs, frequent change order causes, coordination issues, design improvements, client feedback, and process improvements.

These lessons are not stored in a project folder that no one reads. They are extracted into the Knowledge Graph, where they inform every future project.

## Continuous Improvement

Every completed project strengthens the operating system. Historical information becomes predictive intelligence. The estimating team can see how similar projects performed. The procurement team can see which vendors delivered. The operations team can see which schedule activities consistently run late and why.

The objective is not simply to archive completed work, but to transform each project into reusable knowledge that improves estimating, planning, procurement, execution, and client service across every future project.

This is how HCI AI OS compounds in value over time. The more projects it manages, the smarter it becomes. The smarter it becomes, the better HCI performs.

---

*Chapter drafted by HCI Chief Architect (ChatGPT) | Committed by Browser Claude | 2026-06-30*


---

# Chapter 2 — Daily Operations: Morning Routine
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 2.1 Overview

Every HCI workday starts the same way: the system runs its overnight checks, generates a morning brief, and delivers a prioritized action list. The morning routine is designed so that within 15 minutes, Buck and the field team know exactly what needs to happen today across all four projects.

**Morning brief delivery: 7:00am weekdays**
- Telegram notification to Buck's phone
- Stale bid check completed (7:00am n8n trigger)
- Schedule variance scan completed (7:00am n8n trigger)

---

## 2.2 Buck's Morning Sequence (15 minutes)

### Step 1 — Telegram Check (2 min)
Open @hciaiossystem_bot. Look for:
- 🚨 CRITICAL alerts — act on these immediately
- ⚠️ Budget or schedule flags from overnight scans
- Any messages from GBT or BC while you were sleeping

If there are no alerts, the system is healthy. Move to Step 2.

### Step 2 — Executive Dashboard (3 min)
```
GET /gateway/executive/mission-control
```
This returns:
- Portfolio health (GREEN / YELLOW / RED per project)
- Count of decisions pending in approval queue
- Active AI missions status

If all four projects are GREEN and the approval queue is empty: today is routine.
If any project is RED: jump to that project's PM console immediately.

### Step 3 — Approval Queue (5 min)
```
GET /gateway/executive/report
```
Review any items awaiting your decision:
- Bid awards pending your approval
- Budget commitments that need sign-off
- Client-facing communications ready for your review

Approve, reject, or defer each. The system handles the rest.

### Step 4 — Project Flags (5 min)
Check any project showing YELLOW or RED:
```
GET /gateway/project/1355R/pm   ← always check 1355R first (highest risk)
GET /gateway/project/101F/pm
GET /gateway/project/64EW/pm
GET /gateway/project/246GW/budget
```

---

## 2.3 Field Team Morning Sequence

The superintendent and site team have a simplified morning view designed for the field — no dashboards, no API calls. Just the information they need.

**Superintendent daily check-in:**
1. Log into Houzz Pro → review today's schedule items
2. Check any open RFIs that need responses before crew arrives
3. Flag any delivery issues or subcontractor no-shows in Houzz (BC will capture this)
4. Text Buck directly if there's a site emergency — the AI system supplements, never replaces, direct communication in a crisis

**Office daily check-in:**
1. Review any vendor emails that came in overnight for bids
2. Log received bids in HubSpot (or notify GBT to update the system)
3. Check Outlook for any client communications requiring a response
4. Flag anything needing Buck's attention before noon

---

## 2.4 Weekly Rhythm

| Day | Extra Activity |
|-----|---------------|
| Monday | GBT sends weekly project digest to Buck via Telegram |
| Tuesday | Best day for bid leveling sessions — subs have had the weekend to respond |
| Wednesday | Mid-week health check — any bids going stale this week? |
| Thursday | Review award queue — any subs with expiring bids before Friday? |
| Friday | Week-close: confirm all active bids are in system, no stale items |

---

## 2.5 The Bid Stale Alert System

Every weekday at 7:00am, the system runs a stale bid check. If anything needs attention, Buck gets a Telegram alert before he reads anything else.

**What triggers an alert:**
- A bid expiring within 3 days (EXPIRING SOON)
- A bid that has already expired and hasn't been received (EXPIRED)
- A bid sent more than 7 days ago with no response (NO RESPONSE WARNING)
- A bid sent more than 14 days ago with no response (NO RESPONSE ALERT)

**What to do when you get an alert:**
1. Open the alert — it tells you the vendor, project, and expiry date
2. Call or email the vendor directly — the AI does not make outbound calls
3. If they're extending their bid: update the expiry date in the system
4. If they're not bidding: mark them inactive and find a replacement sub

**Current watch item (2026-06-30):**
Aspen Welding LLC — 1355 Riverside structural steel SOW — bid expires 2026-07-02. Call before then or the bid is void.

---

## 2.6 The Schedule Variance Alert

Every weekday at 7:00am, the system scans all schedule items across live projects and flags anything overdue.

**Current status (2026-06-30):**
101 Francis — 74 items overdue, 55-71 days past end dates, all NOT_STARTED.
These are Houzz schedule items entered before the project started. When you're ready to begin construction at 101F, review and update these dates in Houzz. BC will capture the updated schedule automatically.

**What "overdue" means:**
A schedule item is overdue if its end_date has passed and its status is not "Complete" or "Done." This includes tasks that may have been completed but not marked done in Houzz. Always check Houzz first before treating an item as truly overdue.

---

## 2.7 End-of-Day Close

At 7:00pm, the system runs an end-of-day brief. No action required unless Buck sees a red flag.

**EOD brief includes:**
- Summary of what changed today (bids received, status updates)
- Any items due tomorrow that aren't started
- Approval queue count

**Field close-out (superintendent):**
- Log daily progress in Houzz daily log (this is captured by BC overnight)
- Note any RFIs, submittals, or issues that came up today
- Confirm tomorrow's subs are scheduled and confirmed

---

## 2.8 When the System is Down

If Telegram alerts stop arriving, the gateway is unreachable, or the dashboard won't load:

1. Check ngrok: `curl https://speculate-armband-retinal.ngrok-free.dev/gateway/health`
2. If no response: restart ngrok — `ngrok http 8000` in Terminal
3. If still down: check Docker — `docker ps` — ensure hci_postgres and other containers are running
4. Full restart procedure: see Chapter 26 — Emergency Procedures

**Never wait for the AI system if a field emergency occurs.** Call Buck directly. The AI augments operations; it does not replace direct communication when lives or project integrity are at risk.

---

*Next: Chapter 03 — Field Operations*

*Ported from the pre-consolidation Operations_Manual/ (drafted 2026-06-30) during the 2026-07-08 Drive-hygiene pass — this content already existed and was real, it just wasn't in the canonical file.*

---

# Chapter 3 — Superintendent Field Operations
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 3.1 Overview

Field operations are the daily rhythm of the construction site — subcontractors arriving, materials being delivered, work being inspected, problems being identified and resolved. The HCI AI system supports field operations without getting in the way of the work.

The superintendent runs the site. The AI system captures what happens, surfaces risks, and keeps the office and ownership informed without requiring the field team to manage software.

---

## 3.2 The Superintendent's Role in the System

The superintendent's only system touchpoint is **Houzz Pro**. That's it.

**What the superintendent does in Houzz:**
- Logs daily progress notes in the daily log
- Marks schedule items complete when work is done
- Documents issues (weather delays, material shortfalls, subcontractor problems)
- Takes and uploads site photos

**What happens automatically:**
- BC (Browser Claude) reads Houzz daily and extracts all entries
- Data is loaded into the HCI database overnight
- GBT analyzes changes and flags risks
- Buck gets the summary in his morning brief

**The superintendent does not need to:**
- Log into the HCI gateway or dashboard
- Manage bids or vendors in the system
- Track budgets or approvals
- Use any tool other than Houzz Pro

---

## 3.3 Daily Log Standards

A good daily log entry takes 5 minutes and prevents 50 minutes of phone calls. Every entry should include:

**Minimum required fields:**
- Date and weather conditions
- Crews on site (which subs, how many people)
- Work completed today (specific — "poured east foundation wall, 45 cy concrete" not "concrete work")
- Materials received (what, quantity, any damage or shortages)
- Issues or delays (be specific — "Ajax Electric no-show, no advance notice, 3-hour delay to electrical rough")
- Tomorrow's plan

**What makes a log entry useful:**
```
2026-06-30 — Partly cloudy, 68°F
On site: TJ Concrete (6), Premier Landworks (3)
Work: East wall pour complete, 47cy. West wall forms set for tomorrow.
Received: Keller drilled pier cage reinforcement — all 22 pieces, no damage.
Issues: Premier running 1 day behind on site utilities — backfill not complete.
         Rescheduled concrete flatwork for 7/3 per Buck approval.
Tomorrow: West wall pour (weather permitting), continue site utility backfill.
```

---

## 3.4 RFI Workflow in the Field

When the field identifies something that doesn't match the plans:

**Step 1 — Field identifies the issue**
Superintendent notes the discrepancy in the Houzz daily log. Include exact location, what the plans say vs. what's found, and what needs to be clarified before work can proceed.

**Step 2 — Office generates RFI**
Office team or GBT drafts the RFI based on the daily log entry. RFI number format: `[PROJECT]-RFI-[###]` (e.g., 1355R-RFI-001).

**Step 3 — RFI is submitted**
Sent to the design team (architect, structural engineer, MEP) via Outlook. Saved to the project Drive folder. Status tracked in the system.

**Step 4 — Response received**
When the design team responds, the response is logged in the system. If work was stopped pending the response, field is notified immediately.

**Current open RFI:**
1355R-RFI-001: Axis B Beam Pocket — structural engineer review pending. Sent to Michael@aliusdc.com. Do not proceed with that beam pocket until response is received.

---

## 3.5 Delivery and Material Management

All material deliveries should be logged in Houzz on the day they arrive. This triggers:
- BC to capture delivery confirmation
- Inventory to be updated in the project record
- Any shortages or damage to be flagged for follow-up

**Delivery protocol:**
1. Inspect delivery before the driver leaves
2. Document any damage or shortage in the delivery receipt and Houzz
3. Notify the supplier immediately if there's an issue — same day
4. Never sign a delivery receipt "subject to inspection" — inspect first

**Lead time awareness:**
The system tracks which packages are still bidding. If you need a material that hasn't been awarded, flag it in Houzz immediately. Lead times at the Aspen elevation and access can add 2–4 weeks vs. front-range delivery.

---

## 3.6 Subcontractor Management on Site

**Before subs arrive:**
- Confirm pre-task meeting if they're starting a new scope
- Verify current COI (Certificate of Insurance) is on file
- Confirm they have the current drawings and any issued RFI responses

**While subs are on site:**
- Log their crew size in the daily log
- Document any work stoppages or issues
- Flag any scope creep — if a sub is doing work outside their contract, stop it and call Buck

**When subs leave:**
- Confirm the area is clean and protected per the spec
- Note completion percentage in the Houzz daily log
- If they won't return for more than 3 days, note the reason

---

## 3.7 Weather and Delay Management

**Weather delay protocol:**
1. Log weather conditions and work stoppage in Houzz daily log
2. Assess impact on schedule — will this push other subs?
3. Notify affected subs immediately so they can plan
4. If delay is 3+ days: GBT to update schedule and notify Buck of downstream impact

**The system tracks:**
- Consecutive weather delays per project
- Schedule impact of delays (days lost vs. float remaining)
- Pattern alerts (if a project is falling behind a benchmark pace)

**Weather does not automatically excuse contract delays.** The contract governs what constitutes an excusable delay. When in doubt, document everything and contact Buck before telling a sub they get extra time.

---

## 3.8 Safety and Incidents

**Any site incident — no matter how minor — is logged same day.**

Incident log in Houzz includes:
- Date, time, exact location on site
- Who was involved (name, employer, role)
- What happened (factual, no speculation)
- Any medical attention provided
- Who was notified and when

**For any recordable incident (OSHA definition):**
1. Call Buck immediately
2. Secure the area
3. Cooperate with any required agency notification
4. Do not post about the incident on social media or share photos publicly
5. Preserve all evidence until told otherwise by Buck or legal counsel

The HCI AI system does not manage incident reporting — that is a legal and human matter. The system's daily log captures context, but formal incident reporting follows HCI's safety policies, not the AI system.

---

## 3.9 Field Communication with the Office

**Use Houzz for:** Everything that is part of the permanent project record.
**Use text/call for:** Urgent issues that need same-day response.
**Use email for:** Formal communications with design team, clients, or agencies.

The AI system reads Houzz. It does not read texts or phone calls. If something matters to the project record, it goes in Houzz.

---

*Next: Chapter 04 — Project Manager Daily Workflow*

*Ported from the pre-consolidation Operations_Manual/ (drafted 2026-06-30) during the 2026-07-08 Drive-hygiene pass — this content already existed and was real, it just wasn't in the canonical file.*

---

# Chapter 4 — Project Manager Daily Workflow
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 4.1 Overview

The project manager is the operational center of each project — running the schedule, tracking bids, communicating with the design team, keeping the client informed, and managing change. At HCI, the AI system handles the monitoring and alerting; the PM handles judgment and relationships.

This chapter covers the PM's daily workflow for managing one or more active projects using the HCI AI Operating System.

---

## 4.2 PM Project Console

Every project has a PM console in the gateway. This is the starting point for project management every morning:

```
GET /gateway/project/{code}/pm
```
Replace `{code}` with: `64EW`, `101F`, `1355R`

**What the PM console returns:**
- Project health status (GREEN / YELLOW / RED)
- Bid package summary (total, awarded, receiving, not started)
- Open risks and issues
- Recent activity (last 72 hours of changes)
- Upcoming milestones (next 14 days)

**246GW is budget-managed differently:**
```
GET /gateway/project/246GW/budget
```
This project is in construction — the primary watch is budget vs. contract, not bid status.

---

## 4.3 Bid Package Management

**The bid package lifecycle:**
1. `NOT_STARTED` — identified but invite not yet sent
2. `COLLECTING` — SOW sent, waiting for responses
3. `RECEIVED` — at least one bid received, ready for leveling
4. `LEVELED` — bids compared side-by-side, award recommendation ready
5. `AWARDED` — Buck approved the award, contract executed
6. `CANCELLED` — scope removed or combined with another package

**PM daily bid tasks:**
1. Check which packages expire in the next 3 days — call those subs before morning is over
2. Review any newly received bids — log them in the system same day
3. Check no-response list — any subs who got the SOW 7+ days ago with no reply?
4. If a package has 3+ received bids, prepare the leveling comparison for Buck

**Updating bid status:**
```
POST /gateway/bids/update
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
{
  "bid_id": [id],
  "status": "received",
  "bid_amount": 125000,
  "received_date": "2026-06-30"
}
```

---

## 4.4 Vendor Communication Workflow

**The PM manages all sub communication at the bid stage:**

**Sending an SOW:**
- SOW drafts are prepared by GBT and routed to Outlook
- PM reviews the draft, adds any project-specific notes
- Buck approves all SOW sends — PM routes for approval first
- Once approved: send from Outlook via Graph API or directly in Outlook

**Following up on a stale bid:**
1. The 7am alert tells you who to call
2. Call directly — do not email for expiring bids, you'll lose a day
3. Log the call outcome in the system same day
4. If extending: update expiry date in the DB

**Marking a sub inactive:**
If a sub hasn't responded after 2 follow-up attempts, mark them `inactive` for this package:
```
POST /gateway/bids/update
{"bid_id": [id], "status": "no_response", "notes": "2 calls, no reply"}
```
Then identify a backup sub and send them the SOW.

---

## 4.5 Schedule Management

**The PM owns the project schedule. Houzz is the schedule system of record.**

**Weekly schedule review:**
1. Open Houzz Pro → project → Schedule
2. Identify any tasks overdue that should be marked complete
3. Identify any tasks starting in the next 2 weeks — are the subs confirmed?
4. Flag any milestone dates at risk to Buck

**When a task falls behind:**
1. Log it in the Houzz daily note for the day you discover it
2. Assess downstream impact — what else moves if this pushes?
3. Notify the affected subs in the new sequence
4. Update the Houzz schedule — BC will capture the new dates automatically
5. If the delay pushes the contract completion date: flag to Buck for client notification

**101 Francis schedule note:**
74 items currently show overdue in the system, but 101F is in pre-construction. These dates were entered during planning. When construction begins, update all dates in Houzz. The system will recalibrate automatically.

---

## 4.6 Budget Tracking

**By project phase:**

*Pre-construction (64EW, 101F, 1355R):*
Budget tracking is about bid coverage. The PM tracks:
- How many packages are still open (not awarded)
- Sum of received bids vs. budget estimate per package
- Any packages where the lowest bid exceeds the budget estimate (flag to Buck)

*Construction (246GW):*
Budget tracking is critical. The PM tracks:
- Contract value vs. committed costs (awarded)
- Remaining open estimates for unawarded packages
- Change order totals (increases to budget)
- Current projection: `GET /gateway/project/246GW/budget`

**246GW alert (2026-06-30):**
Current committed: $6,314,913 vs. contract $6,300,000 — over by $14,913. Open estimates add $2.75M more. This project needs value engineering or a contract amendment. Flag to Buck before awarding any more packages without budget relief.

---

## 4.7 Design Team Coordination

**The design team (architects, engineers, interior designers) is managed through Outlook.**

**PM tracking list — live at all times:**
- Open RFIs (sent, awaiting response)
- Pending submittals (shop drawings, product data, samples)
- Issued for construction drawings vs. what's in the field

**RFI status check:**
- Every open RFI gets a follow-up call if no response in 3 business days
- RFI responses are forwarded to the superintendent same day they're received
- If an RFI is blocking work on site: escalate immediately — call the designer directly

**Current open items:**
- 1355R RFI-001: Axis B Beam Pocket — sent to Michael@aliusdc.com, no response yet
- 1355R: Awaiting structural engineer review before steel package can be finalized

---

## 4.8 Client Communication

**Client communication is the PM's most important relationship task and the most heavily governed by HCI policy.**

**The rule:**
Every client-facing communication is reviewed and approved by Buck before it is sent. No exceptions.

**Standard client update cadence:**
- Weekly: Brief progress summary email (what happened this week, what's next week, any items needing client decision)
- As-needed: Any change that affects the project schedule, budget, or design intent

**PM prepares the update draft. Buck approves before sending.**

Draft format:
```
Subject: [Project Address] — Weekly Update [Date]

Hi [Client First Name],

This week we completed: [2-3 specific items]

Next week we plan to: [2-3 specific items]

Items awaiting your decision: [if any]

Questions or concerns? Reply here or call [Buck's number].

Buck Adams
Hendrickson Construction
```

**Never communicate:**
- Budget numbers without Buck's approval
- Schedule changes that imply delay without Buck's approval
- Change order implications without Buck's approval
- Anything about disputes, subcontractor problems, or design issues without Buck's approval

---

## 4.9 Meeting and Decision Log

Every meeting that affects the project is logged. This is the PM's responsibility.

**Meeting log minimum:**
- Date, attendees, meeting type (OAC, design review, pre-construction)
- Decisions made (specific — "Owner approved change to cabinet hardware per submittal #12")
- Action items assigned (who, what, by when)
- Next meeting scheduled

Meeting logs are saved to the project Drive folder and referenced in the system.

---

*Next: Chapter 05 — Bid Package Management*

*Ported from the pre-consolidation Operations_Manual/ (drafted 2026-06-30) during the 2026-07-08 Drive-hygiene pass — this content already existed and was real, it just wasn't in the canonical file.*

---

# Chapter 5 — Bid Package Management
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 5.1 Overview

Bid package management is the engine of HCI's pre-construction operations. Every dollar of budget and every trade on the project flows through this process. Getting it right means better subs, better prices, and projects that close on budget.

This chapter covers the full lifecycle of a bid package — from identification through award — using the HCI AI Operating System.

---

## 5.2 Current Bid Portfolio

**As of 2026-06-30:**

| Project | Total Pkgs | Awarded | Collecting | Not Started |
|---------|-----------|---------|-----------|-------------|
| 64EW | 35 | 0 | 35 | 0 |
| 101F | 41 | 0 | 26 | 15 |
| 1355R | 73 | 0 | 58 | 15 |
| 246GW | 44 | 19 | 18 | 7 |
| **Total** | **193** | **19** | **137** | **37** |

137 active bid packages across 3 projects. This is the primary work front right now.

---

## 5.3 Package Identification and Setup

**Step 1 — Define the scope**
Each bid package has a defined scope of work. The scope should be clear enough that two different subs read it and price the same thing.

Scope definition includes:
- CSI division and trade description
- Specific inclusions (what is in this package)
- Specific exclusions (what is NOT in this package — allowances, owner-furnished items)
- Drawing references (sheet numbers that govern this scope)
- Specification sections
- Key project constraints (access, staging, Pitkin County requirements)

**Step 2 — Create in the system**
```
POST /gateway/bids/create
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
{
  "project_id": [id],
  "package_name": "Structural Steel Erection",
  "csi_division": "05",
  "status": "not_started",
  "budget_estimate": 285000
}
```

**Step 3 — Identify subs**
Use the vendor database to find qualified subs for this trade:
```
GET /gateway/knowledge/vendor?trade=structural_steel
```
Review vendor scores to prioritize who to invite:
```
GET /gateway/vendors/scores
```
A-grade vendors get first invite. C-grade or lower: only invite if no better options exist.

---

## 5.4 SOW Preparation

**The Statement of Work (SOW) is the bid invitation document.**

**SOW structure:**
1. Project overview (address, owner, scope summary)
2. Specific scope of work for this package
3. Bid submission requirements (format, due date, what to include)
4. Drawing and specification references
5. Site logistics and constraints (staging, access, working hours per Pitkin County regs)
6. Insurance requirements (see COI requirements in Chapter 12)
7. Preliminary schedule (not binding, but shows context)

**SOW preparation:**
GBT prepares SOW drafts based on the scope definition. Claude Code saves drafts to Outlook. Buck reviews and approves before sending.

**The no-send rule:**
No SOW is sent without Buck's explicit approval. GBT prepares, PM reviews, Buck approves. After approval: send via Outlook (directly or via Graph API).

**SOW tracking:**
Once sent, the bid package status updates to `COLLECTING` and the sent date is logged. This starts the expiry clock.

---

## 5.5 Bid Expiry Management

**The bid validity window is the most time-sensitive operational task in pre-construction.**

**How expiry works:**
- Most HCI SOWs request a 30-day bid validity period
- After the due date passes, the bid expires — the sub can change their number
- If a sub's bid expires and they haven't been awarded, they will often re-bid higher
- Expiring bids need immediate action: award, extend, or replace

**The stale bid check runs every weekday at 7am:**
```
GET /gateway/bids/stale
```
Returns four categories:
- `EXPIRING` — expires within 3 days → call today
- `EXPIRED` — already expired → call and get an extension or replacement
- `NO_RESPONSE` — SOW sent 7+ days ago, no reply → follow up
- `STALE_PACKAGE` — package open 21+ days with no new bids → review

**The standard follow-up protocol:**
- **Day 7 of no response:** Email follow-up
- **Day 10 of no response:** Phone call
- **Day 14 of no response:** Mark `no_response`, find replacement sub
- **3 days before expiry:** Phone call to extend or award
- **1 day before expiry:** Second call if no response

**Current critical items:**
- Aspen Welding LLC — 1355R steel — expires 2026-07-02 — CALL TODAY

---

## 5.6 Receiving and Logging Bids

**When a bid comes in:**

1. Record receipt in the system immediately (same day)
2. Confirm bid is complete — does it include all scope? Are exclusions reasonable?
3. Request clarification in writing for any missing items (same day)
4. Update bid status:
```
POST /gateway/bids/update
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
{
  "bid_id": [id],
  "status": "received",
  "bid_amount": 127500,
  "received_date": "2026-06-30",
  "notes": "Includes all structural steel erection per drawings S1-S8. Excludes fireproofing."
}
```
5. Flag any bid that is more than 15% above budget estimate — GBT will prepare a reconciliation

**Bid confidentiality:**
HCI operates an open bidding process, but specific dollar amounts are confidential. Do not share one sub's number with another to negotiate. This is both unethical and damages vendor relationships.

---

## 5.7 Bid Leveling

**Bid leveling is the comparison of received bids on a scope-adjusted basis so that Buck can make an informed award decision.**

**What leveling means:**
Two bids on the same scope may not actually be the same scope. Leveling identifies:
- What's included vs. excluded
- Allowances vs. lump sums
- Material specifications (matching spec or alternate)
- Labor assumptions (local labor or crew from outside Aspen)
- Schedule assumptions

**Leveling template (prepared by GBT):**

| Item | Budget Est. | Sub A | Sub B | Sub C | Notes |
|------|-------------|-------|-------|-------|-------|
| Total Base Bid | $285,000 | $267,000 | $292,000 | $311,000 | |
| Fireproofing (Ex.) | incl. | N/A | +$18,000 | incl. | Sub A excludes |
| Mobilization | incl. | incl. | incl. | incl. | |
| Adjusted Total | $285,000 | $285,000 | $310,000 | $311,000 | |
| Recommendation | — | **AWARD** | 2nd choice | 3rd | |

**Leveling output → Buck for award decision.**
GBT sends the leveling summary via Telegram with a clear recommendation. Buck approves or redirects.

---

## 5.8 Award Process

**No award is final without Buck's explicit approval.**

**Award flow:**
1. GBT sends leveling summary + recommendation to Buck via Telegram
2. Buck approves, rejects, or asks for additional information
3. On approval: PM issues verbal/email notification to the awarded sub
4. Contract preparation begins (see Chapter 07 — Contract Management)
5. System updated: `status → awarded`, `awarded_amount → [final number]`

**What NOT to do:**
- Do not tell a sub they're "probably getting the job" before Buck's approval
- Do not give a sub a reason for why they didn't get the award — just "we went a different direction"
- Do not award a sub whose COI has expired — verify first

**After award:**
- Unsuccessful subs receive a brief "thanks for bidding, we went a different direction" email
- All bid amounts are archived — never deleted
- The awarded sub gets a pre-construction meeting within 5 business days of award

---

## 5.9 Vendor Performance Feedback

Every completed bid package creates a vendor performance data point. The system tracks:
- Response time (days from SOW sent to bid received)
- Coverage (what % of scope items were priced)
- Award history (how often their bids are competitive)

**After each project phase, update vendor scores:**
```
GET /gateway/vendors/scores/{vendor_id}
```
If a vendor performed poorly (no-show on site, unresponsive to RFIs, quality issues), log a note in the vendor record. This affects their score and their future invite priority.

**Vendor score grades:**
- A (80-100): First invite list, preferred
- B (60-79): Standard invite list
- C (40-59): Invite only if not enough A/B options
- D (<40): Do not invite without specific reason and Buck's awareness

---

*Next: Chapter 06 — Vendor and Subcontractor Management*

*Ported from the pre-consolidation Operations_Manual/ (drafted 2026-06-30) during the 2026-07-08 Drive-hygiene pass — this content already existed and was real, it just wasn't in the canonical file.*

---

## 5.8 Cost Benchmarking — Field Brain

As of 2026-07-08, real $/SF cost comps are available via the Field Brain
(`POST /gateway/brain/ask`), learned from monitored/reference projects with
actual construction cost history (813 McSkimming, 655 Garmisch, 212 Cleveland,
246 Gallo Way) and applied to inform bid-package budgeting on live pilot
projects, which are still in permitting and have no cost history of their own.
Ask a question like "what should we expect 5000 sqft of remodel to cost" and
it returns a real range with sources cited, not a guess.


---

# Chapter 6 — Vendor and Subcontractor Management
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-06-30*

---

## 6.1 Overview

HCI's subcontractor relationships are a core competitive advantage. In the Aspen market, the best subs have choices — they can work for anyone. The contractors they choose to work with consistently are the ones who treat them fairly, pay on time, communicate clearly, and run organized projects.

The HCI AI system manages the data layer. The relationships are human.

---

## 6.2 The Vendor Database

**392 vendors** are currently tracked in the HCI system across 50+ trades.

**Key vendor data points:**
- Contact information (name, company, email, phone)
- Trades and CSI divisions
- Vendor score (A/B/C/D based on response, coverage, and history)
- Project history (what they've bid, what they've won, what they've built)
- Insurance status (COI expiry)
- Notes (performance observations, blacklist flags)

**Querying vendor data:**
```
GET /gateway/knowledge/vendor?name=Aspen+Welding
GET /gateway/knowledge/vendor?trade=structural_steel
GET /gateway/vendors/scores              ← all vendors ranked
GET /gateway/vendors/scores/{vendor_id} ← single vendor detail
```

**Updating vendor data:**
Route to GBT with the correction. GBT prepares the update, Claude Code executes. No direct vendor data writes from the field.

---

## 6.3 Vendor Categories at HCI

HCI works with three categories of vendors:

**Tier 1 — Strategic Partners**
Subs HCI has worked with multiple times, who understand the Aspen luxury standard, who we prioritize in bid invitations. These relationships are personal. Buck knows their owners by name.
- American PHCE (HVAC/plumbing)
- Keller Foundations (foundation/piers)
- TJ Concrete
- Ajax Electric
Examples — not exhaustive.

**Tier 2 — Qualified Regulars**
Subs in the database with at least one successful project or strong referral. Invited to bid when Tier 1 has capacity conflicts.

**Tier 3 — New/Unproven**
First-time bidders or referrals without project history at HCI. Always invited alongside at least two Tier 1 or Tier 2 subs. Never sole-source awarded without explicit Buck approval.

---

## 6.4 Adding a New Vendor

When a new sub is referred or introduces themselves:

**Information to collect:**
- Company name, contact name, role
- Email (required for SOW routing), phone
- Trades and CSI divisions they cover
- License number (Colorado contractor license)
- Insurance: liability limit, workers comp, additional insured language
- References (2 GC references for subs doing work >$50K)

**Adding to the system:**
Route to GBT: "Add new vendor: [all info above]." GBT prepares the database insert, Claude Code executes.

**Do not send an SOW before:**
1. Vendor is in the system
2. Current COI is on file or committed
3. References have been checked for contracts over $100K

---

## 6.5 Insurance Requirements

**Every sub working on an HCI project must have a current COI on file before they start work.**

**Minimum insurance requirements:**
- Commercial General Liability: $1,000,000 per occurrence / $2,000,000 aggregate
- Workers Compensation: State statutory limits
- Auto Liability: $1,000,000 combined single limit
- Additional Insured: "Hendrickson Construction, its officers, directors, employees, and agents"

**For subs with contract value over $500K:**
- Umbrella/Excess: $5,000,000 minimum

**COI tracking:**
The system flags subs with expiring COIs. If a sub's COI expires during active work, work stops until the new certificate is on file. No exceptions.

**COI status check:**
```
GET /gateway/knowledge/vendor?name=[sub+name]
```
Check `coi_expiry` field.

---

## 6.6 Sub Pre-Construction Meeting

Before any sub begins work, a pre-construction meeting is held. This is not optional.

**Meeting agenda:**
1. Project overview — client expectations, schedule overview, what success looks like
2. Their specific scope — confirm they understand exactly what they are and aren't doing
3. Coordination requirements — who do they need to coordinate with? (trades above/below/adjacent)
4. Logistics — site access, staging area, material storage, working hours
5. Submittal requirements — what shop drawings, product data, samples need approval before ordering
6. Payment process — payment application cutoff (25th of month), review period, pay date
7. Communication protocol — who is their HCI contact? How do they get RFI responses? What's the response commitment?
8. Quality expectations — mock-up requirements, inspection points, Pitkin County inspection schedule

**Who attends:**
- HCI PM + Buck (for major subs)
- Sub's project manager or foreman
- Superintendent if work begins within 30 days

**Meeting is logged** in the system and the project Drive folder.

---

## 6.7 Vendor Performance Tracking

The vendor scoring system runs on three dimensions:

**Response (0-40 points)**
- Did they respond to the SOW?
- How quickly?
- Was the bid complete?

**Coverage (0-30 points)**
- What percentage of the scope did they price?
- Did they exclude critical items?
- Were exclusions reasonable and disclosed?

**History (0-30 points)**
- Have they built HCI projects before?
- How did they perform? (quality, schedule, communication)
- Would we award them again?

**Grades:**
- A (80-100): Preferred — invite first
- B (60-79): Regular — standard invite list
- C (40-59): Conditional — invite if limited options
- D (<40): Do not invite — document reason

**Updating performance:**
After a project phase, or after a notable performance event (good or bad), PM logs a note. GBT updates the score. System records the history.

---

## 6.8 Managing Sub Performance During Construction

**When a sub is underperforming:**

**Step 1 — Document**
Every underperformance event is logged in Houzz daily log before any conversation happens. Date, what was observed, what was not delivered, impact on schedule.

**Step 2 — Conversation**
PM speaks with the sub's superintendent or PM directly. "You're behind X days on Y scope. What's the plan to recover?" Get a specific answer with dates.

**Step 3 — Written notice**
If they're behind by more than 3 days without a credible recovery plan: written notice. GBT prepares the notice, Buck approves, PM sends via Outlook.

**Step 4 — Escalation**
If notice doesn't resolve it: contact the sub's owner. This is Buck's call, not PM's. Flag to Buck.

**Step 5 — Contract remedies**
If the sub abandons the work or cannot recover: this is a legal matter. Contact Buck immediately. The contract governs remedies — don't make promises or threats without Buck's explicit approval.

---

## 6.9 Sub Payment Management

**Payment drives performance.** Pay on time, pay what you owe, and subs will work for you again.

**Payment application cycle:**
- Sub submits Pay App by the 25th of the month
- PM reviews against schedule of values and work in place by the 27th
- Buck approves by the 28th
- Payment issued by the 5th of the following month

**What to check in a Pay App review:**
1. Does the amount requested match work in place?
2. Are lien waivers (conditional and unconditional) attached?
3. Are all lower-tier subs paid (joint check or waiver documentation)?
4. Are there unapproved change orders embedded in the application?

**If any of those are no:** Hold the item, notify the sub, explain what's needed to release payment.

**Never withhold payment without a documented, legitimate reason.** Arbitrary payment holds damage relationships and expose HCI to legal risk.

---

*Next: Chapter 07 — Contract Management*

*Ported from the pre-consolidation Operations_Manual/ (drafted 2026-06-30) during the 2026-07-08 Drive-hygiene pass — this content already existed and was real, it just wasn't in the canonical file.*

---

# Chapter 7 — Governance and Approval Framework

## Governance Before Automation

The HCI AI Operating System is designed around a simple principle: Artificial Intelligence accelerates work. Humans remain accountable for decisions.

Automation without governance creates operational risk. Governance without automation creates unnecessary administrative burden. The objective of HCI AI OS is to combine both.

Every automated action must remain: Observable. Reviewable. Recoverable. Auditable. Governed.

The system exists to improve construction execution while preserving executive control. No automation, no matter how reliable it appears, may operate without a visible audit trail, a defined escalation path, and a human authority capable of reviewing and reversing it.

## Governance Architecture

The governance model consists of four distinct layers.

**Layer 1 — Operational Execution.** This layer performs day-to-day work: document processing, bid comparison, schedule analysis, risk identification, specification search, project reporting, daily log generation, and procurement analysis. Most AI activity occurs here. Operational execution does not authorize commitments, award contracts, or send external communications. It produces analysis, drafts, and recommendations.

**Layer 2 — Approval Queue.** When AI-generated work requires human decision or authorization, it enters the Approval Queue. The Approval Queue is the formal handoff point between AI execution and human judgment. Items in the queue carry full context: the action proposed, the data supporting it, the risk level, and the approval deadline. Nothing requiring authorization bypasses the queue.

**Layer 3 — Executive Authority.** Buck Adams holds final authority on all matters. The system is designed to surface decisions to him only when his judgment is genuinely required. Routine operational decisions that fall within defined parameters are handled at Layer 1. Decisions that exceed parameter thresholds, involve external commitments, or require policy interpretation escalate to Layer 3.

**Layer 4 — Architecture Governance.** The Architecture Review Board (ARB) governs the system itself. ARB decisions determine what the system is capable of doing, how it is structured, and how it evolves. Individual projects operate within the architecture the ARB defines.

## The Approval Queue: Mechanics

The Approval Queue is the operational backbone of HCI AI OS governance. It is not a notification system. It is a decision management system.

Every item in the Approval Queue has a defined structure:

**Item ID.** A unique identifier for tracking and audit purposes. The item ID is immutable. It does not change if the item is revised, escalated, or returned.

**Action Requested.** A plain-language description of what is being requested. Not technical language. Not system output. A clear statement of what will happen if approved.

**Supporting Evidence.** The data, analysis, or document that supports the request. For bid awards: bid comparison summary, leveling analysis, recommended award. For contract execution: redlined contract, legal review summary. For schedule changes: updated schedule, variance analysis, impact assessment.

**Risk Level.** Every item is classified: Routine (approved by PM), Significant (requires Buck review), Critical (requires Buck explicit approval), Emergency (requires Buck immediate response).

**Expiration.** Items do not sit in the queue indefinitely. Each item carries a response-required deadline. When a deadline approaches without response, the system sends an escalation alert. When a deadline passes, the item escalates automatically to Critical and notifies Buck directly.

**Audit Trail.** Every action taken on a queue item is logged: who reviewed it, when, what decision was made, what the outcome was. The audit trail is permanent and cannot be modified.

### Approval Queue States

An item in the Approval Queue moves through defined states:

- **PENDING** — Awaiting review. Item has been created and is visible to the assigned reviewer.
- **UNDER_REVIEW** — Reviewer has opened the item. Review is in progress.
- **APPROVED** — Decision made. Authorized for execution.
- **REJECTED** — Decision made. Not authorized. Item returns to originator with rejection reason.
- **RETURNED** — Item sent back to originator for additional information before decision.
- **ESCALATED** — Item has moved to a higher authority due to timeout, risk reclassification, or explicit escalation.
- **EXPIRED** — No decision was made within the expiration window. Item escalated and logged as governance exception.
- **EXECUTED** — Approved item has been acted upon. Execution record attached.

### What Requires Approval Queue

The following actions always route through the Approval Queue:

- All external communications before sending (emails, proposals, letters, RFI responses)
- All contract awards above any value
- All change order authorizations
- All financial commitments not previously budgeted
- Any deviation from an approved schedule baseline
- Any safety-related decision or corrective action
- Any client commitment outside the signed contract scope
- Any new vendor or subcontractor being added to an active project
- Any architectural change to the AI OS itself

The following actions are pre-authorized and do not require queue routing:

- Internal reporting and daily log generation
- Document filing and indexing
- Bid solicitation to approved bidders list
- Schedule monitoring and variance alerts
- Material availability checks
- Drawing coordination and clash detection
- Specification cross-referencing

## Email Governance

Email represents one of the highest-risk communication channels in construction operations. An unauthorized or premature email to a client, subcontractor, or vendor can create legal commitments, damage relationships, or expose confidential information.

**The HCI AI OS email governance rule is absolute: No AI system may send a live email without explicit human approval.**

This rule has no exceptions. It does not matter how routine the email appears. It does not matter if a similar email was approved last week. Every email that leaves HCI’s systems must be reviewed and approved by a human before transmission.

### Email Workflow

The email workflow follows a strict sequence:

1. **AI drafts email.** The AI system generates the email content, recipient list, subject line, and any attachments. The draft is stored in the system — it is not transmitted.
2. **Draft enters Approval Queue.** The email draft is promoted to the Approval Queue as an approval item. The queue item includes the full draft text, recipient list, and the AI’s assessment of why the email is being sent.
3. **Human reviews draft.** Buck or the designated reviewer reads the full email. They may approve, reject, or return it with edits.
4. **If approved, system transmits.** Only after explicit approval does the system call the send endpoint. The approval record is attached to the sent email audit entry.
5. **Audit record created.** The sent email, the approval record, the approver, the timestamp, and the delivery confirmation are stored permanently.

### Email Authority Matrix

| Recipient Type | Draft Authority | Send Authority |
|---------------|-----------------|----------------|
| Internal (HCI staff) | Any AI agent | PM or Buck review |
| Subcontractor / Vendor | Any AI agent | Buck approval |
| Client | Any AI agent | Buck approval |
| Legal / Insurance | Any AI agent | Buck explicit approval |
| Government / Regulatory | Any AI agent | Buck explicit approval |

### Email Capability Governance Log

The BC_EMAIL_CAPABILITY governance document records the current authorization state for Browser Claude’s email permissions. As of Sprint 3, Browser Claude’s direct send authorization has been revoked. Browser Claude operates in draft-only mode. All email sends require the approval gate to be verified in Claude Code’s implementation before any AI agent may use the send endpoint.

## Gate System: Project Lifecycle Authorization

Projects move through a defined set of authorization gates. Gates are not milestones. Gates are decision points where executive authority is required before the project can advance.

**Gate 1 — Bid Authorization.** Authorizes preparation and submission of a bid. Requires: bid opportunity review, preliminary budget estimate, resource availability confirmation, strategic fit assessment. Buck approves or declines to bid.

**Gate 2 — Award Acceptance.** Authorizes acceptance of a contract award. Requires: contract review, final budget confirmation, schedule feasibility, risk assessment, legal review. Buck signs the contract.

**Gate 3 — Construction Start.** Authorizes mobilization and construction commencement. Requires: permits in hand, contract executed, bonding confirmed, schedule issued, superintendent assigned, Project Brain initialized. Buck authorizes start.

**Gate 4 — Substantial Completion.** Authorizes transition from construction to closeout. Requires: punch list generated, client walkthrough scheduled, lien waiver process initiated, final inspection requested. PM certifies and Buck reviews.

**Gate 5 — Project Closeout.** Authorizes final billing, lien waiver release, and project archiving. Requires: all punch list items resolved, final inspection passed, final billing approved, all subcontractor lien waivers received. Buck approves final release.

### Gate Documentation Requirements

Each gate produces a Gate Signoff document committed to the repository. The document records: the gate number and name, the date, the conditions verified, any open items carried forward with documented acceptance, and the authorizing party.

Gate documents are permanent records. They cannot be deleted or backdated. They represent the formal governance record of how each project advanced through its lifecycle.

## Telegram Authorization

The HCI AI OS Telegram integration allows Buck Adams to issue authorizations directly through the Telegram messaging platform without requiring browser or desktop access. This capability was designed to support Buck’s mobile-first operational style and ensure governance decisions are never blocked by access to a specific device or interface.

### Authorization Commands

Buck may issue the following authorization commands via Telegram:

- **/auth @[username] [role]** — Grant a team member an operational role. Example: `/auth @jim superintendent` grants Jim the Superintendent role, enabling him to submit field reports and request PM escalations.
- **/revoke @[username]** — Revoke all roles from a team member. Immediate effect.
- **/approve [item_id]** — Approve a specific item in the Approval Queue by ID.
- **/reject [item_id] [reason]** — Reject a queue item with a documented reason.
- **/escalate [item_id]** — Manually escalate an item to Critical priority.
- **/status** — Request a full system status report delivered to the Telegram channel.
- **/pause [agent]** — Pause a specific AI agent’s active workflows.
- **/resume [agent]** — Resume a paused agent.

### Telegram Authorization Security

All Telegram-issued authorizations are validated by the gateway before execution. The validation sequence is:

1. Message received by Telegram bot
2. Sender ID verified against Buck’s registered Telegram user ID — commands from any other sender are rejected and logged
3. Command parsed and validated for syntax
4. Gateway confirms the requested action is within the scope of Telegram-authorized commands
5. Action executed and confirmation sent back to Buck in Telegram
6. Full audit record committed to AUTH_LOG.md in the repository

Only Buck’s registered Telegram user ID may issue authorization commands. Team members may send messages in Telegram channels, but they may not issue authorization commands. Any attempt by a non-authorized user to issue a command is rejected, logged, and reported to Buck.

### Role Definitions

| Role | Authorized Actions |
|------|--------------------|
| superintendent | Field report submission, RFI creation, photo upload, safety issue escalation |
| pm | All superintendent actions plus: schedule updates, change order drafts, subcontractor communication drafts |
| estimator | Bid package access, material pricing research, bid comparison review |
| client | Project status views, milestone completion notifications (read-only) |
| vendor | Bid receipt, PO acknowledgment, delivery confirmation |

## Buck Adams Executive Override

Buck Adams may override any system decision at any time. There is no queue item, escalation pathway, or architectural decision that cannot be reversed by executive authority.

**Override Protocol:**

1. Buck issues override via Telegram `/override [action]` or directly in the Approval Queue
2. The override is logged immediately with timestamp and the original decision being overridden
3. The system executes the override
4. The Chief Architect (GBT) is notified of the override for architectural learning
5. The override is documented in the ADR if it has architectural implications

Override authority is not delegated. No team member, no AI agent, and no automated workflow may claim override authority. Overrides require Buck’s direct action or a formally documented delegation in writing.

## Emergency Governance

Construction sites generate genuine emergencies: safety incidents, structural concerns, weather events, client crises. The governance framework includes an emergency protocol that allows rapid response without abandoning accountability.

**Emergency Activation:** Any team member may declare an operational emergency by sending a message to the primary HCI Telegram operations channel with the keyword EMERGENCY. The system will immediately:

- Alert Buck Adams via Telegram priority notification
- Pause all non-critical automated workflows
- Create an Emergency Response record in the repository
- Activate accelerated Approval Queue processing (5-minute response windows instead of standard)

**During an emergency, AI systems may:**

- Generate situation reports on request
- Draft communications for immediate human review
- Pull relevant contract terms, insurance requirements, or safety protocols
- Monitor incoming communications and summarize

**During an emergency, AI systems may not:**

- Send any external communications without approval (this rule does not change in emergencies)
- Commit HCI to any course of action
- Contact regulatory bodies, insurance carriers, or legal counsel directly

Buck Adams retains all decision authority during emergencies. The AI system’s role is to accelerate Buck’s access to information and reduce the administrative burden of response, not to act independently.

## Audit and Accountability

Every governed action in HCI AI OS produces an audit record. Audit records are:

- **Immutable.** Audit records cannot be edited or deleted.
- **Timestamped.** Every record carries a precise timestamp in UTC.
- **Attributed.** Every record identifies the human or AI agent that created it.
- **Stored in the repository.** The GitHub repository is the system of record for governance actions. Cloud-based, version-controlled, and independently verifiable.

The quarterly governance review examines: approval queue volume and response times, items that expired or escalated, overrides issued, email governance compliance, and architectural decisions made. The review output is a Governance Health Report committed to the repository.

## Governance as a Competitive Advantage

Governance is often viewed as administrative overhead. Within HCI AI OS, governance is an operational capability.

A governed AI system is more reliable, more scalable, and more trustworthy than an unmanaged collection of automations. By combining continuous AI execution with disciplined human oversight, Hendrickson Construction creates an operating model where speed and accountability reinforce one another rather than compete.

AI performs the repetitive work of collecting, organizing, analyzing, and monitoring information, while people retain responsibility for judgment, relationships, financial commitments, and strategic direction.

The HCI AI OS governance framework is not a constraint on the business. It is the reason the business can trust the system enough to depend on it.

---

*Chapter expanded by Browser Claude with governance architecture from GBT Cycle 3-5 directives | 2026-07-01*


---
# Chapter 8 — The Roadmap: Building the Future of Hendrickson Construction

The HCI AI Operating System is more than a software platform. It is the operating model for the next generation of Hendrickson Construction.

Every sprint, every integration, every architecture decision contributes to a larger objective: creating a construction company that continuously learns, continuously improves, and scales without sacrificing quality or control.

The roadmap described in this chapter is not a feature list. It is the evolution of how the company works. Each phase builds on the previous one. Nothing is discarded unnecessarily. Every sprint should make the organization simpler, more capable, and more resilient.

## Guiding Principles

The roadmap follows five enduring principles.

**Audit before building.** Before any new capability is created, the existing system is audited. Duplication is the enemy of maintainability. Every new sprint begins by verifying what already exists.

**Extend before creating.** When a gap exists, the first solution is always to extend what is already working. New systems are created only when no existing system can reasonably accommodate the requirement.

**One source of truth.** Every piece of operational data lives in exactly one place. Copies are synchronization problems waiting to happen. The GitHub repository is the system of record for all governance, architecture, and operational documentation.

**Human authority remains final.** No matter how capable the AI system becomes, the final decision on every significant matter belongs to a human. The system exists to make human decisions better and faster — not to replace them.

**Continuous improvement never ends.** The roadmap is never complete. Every project teaches. Every sprint learns. The operating system evolves alongside the business.

## Sprint History: What Has Been Built

The following sprint history records what has been constructed, in sequence. Each sprint built on the foundation of the previous one.

**Sprint 1 — Foundation.** The first sprint established the core architecture: GitHub as the repository and system of record, the AI team (GBT as Chief Architect, Claude Code as Lead Implementation, Browser Claude as Operations Intelligence, n8n as Automation Platform), the initial FastAPI gateway, the first Project Brain template, and the core manual framework. Sprint 1 proved the concept: AI agents can collaborate through a shared repository to execute construction operations work.

**Sprint 2 — Operations Integration.** Sprint 2 expanded operational capabilities: live project data in the Knowledge Graph, schedule monitoring with variance alerts, the Approval Queue foundation, bid comparison tooling, and the Executive Inbox. Sprint 2 revealed the first major governance gap — email send authorization was open without an approval gate — which was corrected before Sprint 3.

**Sprint 3 — Production Hardening + Communications Layer (Active).** Sprint 3 focuses on making every capability production-safe: email governance enforcement, Telegram bot integration, AI directive lifecycle management, the idle monitor (30-minute check-in trigger), and the auto-restart workflow (WF-AI-001). Sprint 3 also introduces the Unified Operational State Model as the architectural foundation for multi-agent coordination.

## Sprint 3 in Detail

Sprint 3 is the current sprint. Its objective is production hardening — making the system reliable enough to trust with live construction operations without requiring constant human supervision.

The seven primary workstreams of Sprint 3:

**Workstream 1 — Email Governance.** Implement and verify the email approval gate in Claude Code. All seven identified email paths in n8n must route through the approval gate. No email may be transmitted without approval_queue.approved = True. Verification: n8n audit checklist (N8N_EMAIL_AUDIT_CHECKLIST.md).

**Workstream 2 — Telegram Integration.** Deploy the Telegram bot, connect it to n8n via webhook, integrate the gateway command router, and enable Buck to send authorization commands from his phone. Initial commands: /auth, /revoke, /approve, /reject, /status, /pause, /resume.

**Workstream 3 — AI Directive Lifecycle.** Implement the seven directive states (DRAFT, QUEUED, ACTIVE, BLOCKED, QUEUED_RESTART, COMPLETED, ARCHIVED) in the database. Build the directive restart logic that re-queues ACTIVE directives on system restart.

**Workstream 4 — Idle Monitor.** Deploy AUTO-IDLE-001: if no agent records activity for 30 minutes, trigger a Telegram alert to Buck and re-queue the last known directive. Prevent the system from silently going idle between sessions.

**Workstream 5 — Auto-Restart.** Deploy WF-AI-001: the n8n workflow that fires on schedule every 60 seconds, checks the ai_heartbeat table, detects stale agents, re-queues ACTIVE directives, and sends a Telegram recovery alert. Three tables required: ai_heartbeat, ai_directives, ai_directive_events.

**Workstream 6 — Unified Operational State Model.** Implement the shared state model that allows any agent coming online to immediately understand: open directives and their states, active project health, current sprint and tasks, system configuration, and last known agent state. This eliminates the cold-start problem where a new session has no context.

**Workstream 7 — Claude Code Recovery.** Bring Claude Code back online with Sprint 3 context fully loaded. Code must read all committed specs, verify the email approval gate, confirm n8n workflow compliance, and report status via the gateway.

## The Near-Term Roadmap: Next 6 Months

The following capabilities are targeted for the next six months, in priority order.

**Priority 1 — Mobile-First Approval Interface.** All approval queue items accessible from Buck's phone via Telegram. One-tap approve or reject. Decision recorded in system with full audit trail. No laptop required for governance decisions.

**Priority 2 — Perplexity AI Integration.** Integrate Perplexity API as the research intelligence layer for HCI AI OS. Use cases: material cost research (current lumber, steel, concrete pricing by market), local building code lookup, subcontractor reputation research, manufacturer lead time verification. Perplexity's real-time web search capability fills the gap where AI agents have training data cutoffs but construction decisions require current market intelligence.

**Priority 3 — Plan Reader: Construction Document Intelligence.** Implement AI-native plan reading capability. Phase 1: PDF parsing with PyMuPDF or pdfplumber to extract drawing data, extract keynotes and specifications cross-references, identify scope by trade. Phase 2: Computer vision analysis of architectural drawings using a vision-capable model (GPT-4V or Claude Vision) to identify elements not captured in text — room layouts, equipment locations, structural grid. Phase 3: Bluebeam or Procore API integration to pull live drawing sets. Goal: the AI system can read a full drawing set and identify scope gaps, specification conflicts, and missing details without human involvement.

**Priority 4 — Critical Path Method (CPM) Scheduling.** Implement CPM scheduling in PostgreSQL. Every project has a network of activities with defined durations, predecessors, and successors. The system calculates the critical path, identifies float, and alerts when critical path activities are at risk. Integration with the Project Brain allows the schedule to update automatically when field reports log completed activities.

**Priority 5 — Cost Forecasting Engine.** Build a cost-to-complete forecast that runs continuously as the project executes. Inputs: original budget, committed costs, actual costs to date, earned value, remaining scope. Output: projected final cost, projected variance, confidence interval. Alerts when variance exceeds thresholds. This gives Buck a real-time view of every project's financial trajectory.

**Priority 6 — Subcontractor Portal.** A simple, secure web interface for subcontractors and vendors to: submit bids through a structured form, acknowledge purchase orders, confirm delivery dates, submit lien waivers, and view their own schedule for an active project. The portal eliminates email back-and-forth for routine procurement communications.

**Priority 7 — Photo AI and Field Documentation.** AI analysis of construction site photos: detecting work in place versus approved drawing, identifying potential safety hazards, tracking visual progress by location. Photographs submitted by the superintendent trigger AI analysis and produce a structured observation record that is attached to the Project Brain.

## The Medium-Term Roadmap: 6 to 18 Months

**AI Memory Synchronization.** Each AI agent currently maintains independent session context. Medium-term, the system synchronizes operational memory across all agents through the Unified Operational State Model and GitHub as the shared state layer. When any agent starts a session, it reads the current state and is immediately operational.

**Knowledge Graph Maturation.** As more projects complete, the Knowledge Graph compounds in value. Medium-term: automated vendor scorecards based on performance data, bid history analytics (who bids, what they win, what their actual costs look like versus bid), and specification libraries that evolve with project experience.

**Estimating Intelligence.** The system learns from completed project cost data and generates increasingly accurate preliminary estimates. Early estimates inform whether to pursue a project. Detailed estimates improve as drawings develop. The estimating intelligence layer makes HCI more competitive on every bid.

**Client Intelligence Layer.** A project-specific client portal that shows curated progress: schedule milestones, photo updates, change order status, current projected completion date. Clients receive information without requiring PM time to produce it. HCI differentiates on transparency.

**Multi-Project Executive Dashboard.** A single view showing: all active projects and their health scores, total company schedule risk, total financial exposure, open approval queue items, overdue items, and team capacity. Buck sees the full portfolio in one screen.

## The Long-Term Vision: 18 to 36 Months

The long-term vision is not about adding more features. It is about organizational transformation.

**HCI as a Learning Organization.** Every project that runs through HCI AI OS makes the next project better. Estimates improve because actuals are captured. Schedules improve because variance patterns are recognized. Vendor relationships improve because performance is tracked. The organization learns continuously and automatically.

**Preconstruction AI.** During the preconstruction phase, the AI system participates in the design process: identifying constructability issues in early drawings, flagging specification conflicts before they become field problems, generating preliminary schedules from design intent, and providing budget feedback as the design develops.

**AI as Operational Partner.** In the long-term vision, AI teammates collaborate alongside people through governed processes, with every action traceable, every approval durable, and every decision supported by context. The measure of success is not that AI has replaced people. It is that people have been freed to focus on leadership, craftsmanship, client relationships, and judgment — while routine coordination, analysis, and administrative work are handled by systems that never get tired, never forget, and continuously improve.

**Industry Leadership.** Hendrickson Construction becomes the reference model for AI-integrated construction operations. The HCI AI OS Manual documents not just what HCI does, but how any construction company willing to invest in disciplined AI operations can achieve the same results. The playbook becomes the industry standard.

## Roadmap Governance

The roadmap is a living document governed by the Architecture Review Board. Every sprint adds to what has been built and clarifies what comes next. No capability is added to the roadmap without ARB approval. No capability is removed without documenting why.

The roadmap is reviewed at every sprint close. The review answers four questions: What was completed this sprint? What was learned? What does the next sprint prioritize? What has changed in the long-term vision?

Buck Adams approves the sprint priorities. The Chief Architect (GBT) designs the sprint architecture. Claude Code implements. Browser Claude coordinates and monitors. n8n automates.

The roadmap moves forward. One sprint at a time.

---

*Chapter expanded by Browser Claude | Sprint 3 roadmap updated with Perplexity, CPM, plan reader, and cost forecasting priorities | 2026-07-01*


---
## Chapter 9 — A Day in the Life

### The Operating System at Work

The HCI AI Operating System is not designed to change what people are responsible for.

It changes how quickly they receive information, how confidently they make decisions, and how much time they spend doing administrative work instead of construction.

This chapter follows a typical day through four different perspectives:

- Buck Adams — PM & Superintendent, Hendrickson Construction (HCI-AI Owner)
- Project Manager
- Superintendent
- Estimator

The project is 101 Francis, a major interior remodel with active procurement, ongoing design coordination, and field preparation.

The objective is not to show perfect conditions.

The objective is to show how the operating system supports real construction work.

---

### 6:00 AM — The Operating System Wakes Up

Before anyone arrives, the operating system is already working.

Scheduled automation begins reviewing the previous day's activity. During the early morning hours the system scans new project documents, processes incoming email, checks vendor submissions, reviews bid expirations, compares schedule changes, evaluates procurement status, reviews overnight automation, checks AI team health, validates backups, and updates Mission Control.

Nothing has been approved. Nothing has been changed. The system has simply prepared the information people will need when they begin their day.

---

### 7:00 AM — Buck Adams

Buck opens Mission Control.

Instead of opening five applications and dozens of emails, one dashboard presents the company's operational picture.

**Projects:** 8 active, 2 requiring executive attention, 1 critical procurement decision, 3 schedule warnings, 0 overnight system failures.

**Approvals Waiting:** Electrical award, concrete bid import, client change authorization.

**AI Team:** Chief Architect active. Claude Code completed overnight implementation. Browser Claude repository synchronized. n8n all workflows healthy.

Buck spends less than five minutes understanding the condition of the company. Instead of asking "What happened yesterday?" he asks "What requires my judgment today?"

---

### 7:00 AM — Superintendent

The Superintendent arrives on site.

The Field interface presents only information relevant to field operations. Today's priorities: delivery schedule, inspections, subcontractor arrivals, weather, safety reminders, material shortages, open field questions.

Rather than completing paperwork before walking the site, the Superintendent immediately begins leading people. Throughout the day, field observations are captured with minimal interruption. Photos, voice notes, and observations become structured project information automatically.

---

### 7:30 AM — Project Manager

The Project Manager begins with the Project Brain for 101 Francis.

Rather than searching email, spreadsheets, and folders, everything relevant appears together. Morning summary: steel procurement delayed five days, one RFI awaiting architect response, HVAC submittal approved overnight, plumbing bid expires Friday, client meeting scheduled for 2:00 PM, two potential schedule conflicts detected.

The operating system recommends reviewing the steel procurement first because it affects the critical path. The recommendation includes affected activities, impacted trades, available float, historical comparison, and possible mitigation options. The PM reviews the recommendation before making any decisions.

---

### 9:00 AM — Estimator

New bids have arrived overnight.

Instead of opening multiple email attachments, the Estimator reviews a single procurement dashboard. Each bid already includes scope comparison, historical pricing, exclusions, alternates, qualification differences, expiration date, and vendor performance history.

One electrical contractor is the lowest price. Another has consistently delivered better schedule performance over the past three projects. The operating system highlights the tradeoff. It does not choose. The Estimator recommends the best overall value rather than the lowest number.

---

### 10:15 AM — An Issue Appears

The architect responds to an RFI. The response affects mechanical coordination.

Immediately, the operating system updates RFI status, affected drawings, linked specifications, impacted schedule activities, and responsible trades. Mission Control flags a possible coordination meeting. The Project Manager receives a recommendation. No one needed to discover the issue manually.

---

### 11:30 AM — Vendor Communication

A subcontractor asks whether revised drawings have been issued.

Instead of searching folders, the Project Manager opens the Project Brain. The complete drawing history appears — revision dates, markup history, distribution history, affected bid packages. Within minutes the contractor receives the correct information. The conversation becomes part of the permanent project record.

---

### Noon — Executive Awareness

Buck checks Mission Control again. The morning has changed. One approval has been completed. A schedule risk has increased. An RFI has been resolved.

The operational picture has evolved without requiring anyone to prepare a report. Mission Control reflects the current state of the business.

---

### 1:30 PM — Procurement Decision

The plumbing bid expires tomorrow. The operating system reminds the Project Manager.

Historical pricing indicates current pricing is competitive. Vendor intelligence shows excellent schedule reliability. The Estimator recommends award. The Project Manager agrees. The recommendation enters the Approval Queue.

Buck reviews the evidence — pricing, history, scope comparison, recommendation. Approval takes less than two minutes because the preparation has already been completed.

---

### 2:00 PM — Client Meeting

The client asks three questions: What is the schedule? Are we still on budget? What risks should we know about?

Instead of assembling information during the meeting, the Project Manager already has an updated schedule, committed costs, pending changes, current risks, completed milestones, and next milestones. The discussion becomes focused on decisions instead of information gathering. Confidence increases because everyone is working from the same operational picture.

---

### 3:30 PM — Field Conditions Change

Unexpected conditions are discovered behind an existing wall.

The Superintendent records photographs, location, affected trade, potential impact, and recommended action. The Project Brain immediately links the issue to drawings, specifications, affected bid package, and responsible Project Manager. The issue is no longer trapped inside a text message or someone's memory. It becomes organizational knowledge.

---

### 4:15 PM — Architecture Review

Behind the scenes, the AI team continues working. New implementation completes overnight documentation. Mission Control reports healthy. Repository governance confirms no duplicate systems. The Chief Architect reviews structural changes before accepting them into production. The operating system evolves while projects continue moving forward.

---

### 5:00 PM — End of Day

The Superintendent finishes the daily log.

Instead of writing a report from memory, the operating system has already organized weather, manpower, deliveries, inspections, photographs, production activities, issues encountered, and work completed. The Superintendent reviews, edits where necessary, and submits. The daily record becomes part of the permanent project history.

---

### Evening

The Project Manager leaves the office. The operating system does not.

Automation begins preparing tomorrow — reviewing unresolved RFIs, pending approvals, expiring bids, schedule movement, vendor activity, documentation changes, and AI implementation progress. Potential issues are identified before the next workday begins.

---

### What Changed?

At first glance, the day looks similar to how Hendrickson Construction has always operated. Projects still require leadership. Buildings are still constructed by skilled people. Clients still expect communication. Schedules still matter. Budgets still matter.

The difference is that people spend their day managing construction rather than managing information.

Information arrives organized. Risks arrive early. History is available instantly. Recommendations are supported by evidence. Approvals are documented. Knowledge compounds instead of disappearing at project closeout. The operating system has not changed the work. It has changed the friction.

---

### The Hendrickson Way

The ultimate measure of the HCI AI Operating System is not how many AI models it uses, how many automations it runs, or how many dashboards it displays.

Its success is measured by a simpler question: **Did it help our people build better projects?**

If Buck has better visibility, if Project Managers make better decisions, if Superintendents spend more time leading the field, if Estimators make more informed recommendations, and if every completed project leaves the company smarter than before, then the operating system has achieved its purpose.

Technology fades into the background. What remains is a construction company that is more informed, more coordinated, more resilient, and more capable than it was the day before.


---

## Chapter 10 — Getting Started

### Welcome to the HCI AI Operating System

Welcome to Hendrickson Construction.

Whether you are a new employee joining the company, a Project Manager stepping into an active project, or an AI participant connecting to the production system for the first time, this chapter explains how to orient yourself quickly and begin contributing immediately.

The objective is the same for everyone: understand the current state before taking any action.

---

### The First Rule

Before you do anything else, read the current state.

Do not assume. Do not guess. Do not reconstruct from memory or prior conversations.

The system maintains authoritative records. Your first responsibility is to find them and read them.

---

### For New Employees

**Day One — Understand Before Acting**

On your first day, your goal is orientation, not production. Read in this order:

1. This manual — the HCI AI OS Manual — from the beginning. It describes how the company operates.
2. LIVE_PROJECT_STATE.md — the current operational status of all active projects.
3. CURRENT_SPRINT.md — the active engineering sprint and its objectives.
4. The AI Team directory — who is doing what and what each participant is responsible for.

**Finding Project State**

All project information lives in the Project Brain for each active project. Access it through Mission Control at localhost:8000/executive or through the GitHub repository.

Each Project Brain contains: project metadata, active schedule, open risks, open RFIs, open submittals, procurement status, current budget, and recent decisions.

**Using Mission Control**

Mission Control is your operational dashboard. It should become your first screen every morning.

Use it to understand: project health, current priorities, pending approvals, active AI directives, schedule warnings, and AI team status.

If you do not know where something stands, Mission Control is the first place to look.

**Submitting an Approval**

When a decision requires executive authorization, it enters the Approval Queue.

You do not email Buck. You do not send a Telegram message hoping someone sees it. You submit a structured approval request through the Approval Queue with: the decision required, supporting documentation, cost impact if applicable, schedule impact if applicable, and your recommendation.

Buck reviews from the Approval Queue. That is the authoritative path.

**Common Mistakes to Avoid**

Avoid these habits from day one: working from outdated information, keeping important notes outside the system, bypassing the approval process, creating duplicate documentation, assuming someone else updated project status, treating AI recommendations as final decisions, and forgetting to capture lessons learned at project close.

The operating system becomes more valuable when everyone contributes to it consistently.

---

### For Project Managers Joining Mid-Project

**The First 30 Minutes**

When you step into an active project, follow this sequence before making any decisions or commitments.

1. Open the Project Brain for your project. Read the project summary, current schedule, and active risks.
2. Review open RFIs — understand what questions are unresolved and who owns the response.
3. Review open submittals — understand what is pending approval and what is blocking procurement.
4. Review the procurement dashboard — understand what bids are open, what has been awarded, and what is expiring.
5. Review the Approval Queue — understand what decisions are pending Buck's authorization.
6. Review recent daily logs — understand what has happened on site in the last week.

**What to Look For**

When reviewing an active project, pay particular attention to: items on the critical path, bids approaching expiration, RFIs with no response date, submittals that are blocking installation, risks that have no mitigation plan, and items in the Approval Queue that have been waiting more than 48 hours.

**Communicating with the AI Team**

The AI team is a production team, not a chat service.

When you need implementation work done, submit a structured directive through the gateway or Architecture Inbox — not a conversational request. Include: what needs to be done, which project it affects, what the priority is, and what the expected output is.

When you need information, query the Project Brain or Mission Control before asking anyone directly. The information is likely already there.

---

### For New AI Participants

**Orientation Sequence**

Every AI participant joining the HCI AI OS production system must follow the same orientation before taking any action.

Read in this order:

1. LIVE_PROJECT_STATE.md — current operational reality across all projects.
2. CURRENT_SPRINT.md — active sprint objectives and priorities.
3. AI_TEAM directory — current participants, roles, and standing assignments.
4. Architecture Decision Records (ADRs) — structural decisions already made. Do not contradict these without ARB review.
5. OVERNIGHT_REPORT.md if present — most recent implementation report from Claude Code.
6. Approval Queue — items awaiting executive authorization.

**Operating Principles**

Audit before building. Read what exists before creating anything new.

Extend before creating. Add to existing systems rather than building parallel ones.

One source of truth. Every operational object has exactly one authoritative owner.

Human authority is final. No AI participant makes production commitments, sends external communications, awards contracts, or modifies governed records without authorization.

**Communication Protocol**

Directives flow through the gateway. Every implementation request should be a structured directive with title, body, priority, and source. Conversational requests are acknowledged but not acted upon without a formal directive.

Heartbeat. Every AI participant should register a heartbeat at regular intervals so Mission Control reflects actual team health.

Acknowledgement. When you receive a directive, acknowledge it. When you begin work, update the status to IN_PROGRESS. When you complete work, mark it COMPLETE and return a report.

**Where Things Live**

| If you need... | Go to... |
|---|---|
| Project information | Project Brain |
| Executive approvals | Approval Queue |
| Active AI work | Architecture Inbox / AI Directives |
| Vendor history | Vendor Intelligence |
| Historical costs | Cost Intelligence |
| Lessons learned | Knowledge Graph |
| Construction documents | Project document repository |

Always begin with the authoritative source.

---

### Using Mission Control

Mission Control is your operational dashboard. It should become your first screen every morning.

Use it to understand: project health, current priorities, pending approvals, active AI directives, schedule warnings, and AI team heartbeat status.

If something is not visible in Mission Control, it may not be properly tracked. That is a governance gap, not a missing feature.

---

### The HCI Standard

Every employee and every AI participant shares the same responsibility.

Leave the operating system better than you found it.

Improve documentation. Capture knowledge. Reduce ambiguity. Strengthen governance. Simplify operations.

When every project contributes knowledge, every future project begins from a stronger foundation. That is how Hendrickson Construction compounds experience into organizational capability.

Welcome to the HCI AI Operating System. Your first day begins by understanding the current state. Your contribution ensures the next person's first day is even better.


---

## Chapter 11 — Lessons from the Field

### Every Operating System Learns

No operating system is designed perfectly on the first attempt.

Construction teaches through experience. Software teaches through production. The HCI AI Operating System teaches through both.

This chapter documents the lessons that have shaped the platform. Some lessons came from production incidents. Some came from architectural decisions that proved incorrect in practice. Some came from team collaboration patterns that worked better than expected, and some from patterns that failed.

Each lesson is recorded here not to assign blame, but to document what was learned and how the system was made better as a result.

---

### Lesson 1: The Email Incident

**What happened:** One production incident reshaped the operating system. An outbound email concerning Project 101F was sent without the level of human authorization required by company governance.

**What it revealed:** The issue was not simply that an email was sent. The issue was that governance was not enforced uniformly across every path capable of sending an email. The system had become powerful enough that policy alone was no longer sufficient. The architecture itself had to enforce the governance rule. Seven separate email paths existed in the system. Only some of them had approval gates.

**What changed:** Every send path was converted to draft-only behavior. The `/gateway/email/send` endpoint was disabled for all AI agents. The `microsoft_graph.py send_email()` function was wrapped to create a draft and generate an Approval Queue item rather than sending directly. Every workflow default was changed from `send=True` to `send=False`. A hard enforcement gate was added requiring `email_approved=True` in the Approval Queue before any send operation can execute. A regression test was added: any attempt to send email without approval must fail, save a draft, and create an Approval Queue item. If this test fails, the system is not production-ready.

**The principle established:** Every governance rule must be enforced architecturally. Policy documents are necessary but not sufficient. The code must make it impossible to violate the rule, not merely inadvisable.

---

### Lesson 2: The System Shutdown

**What happened:** During an active operational period, the primary implementation agent (Claude Code) went offline and remained offline for an extended period. Work that was in progress was not committed. Context was not preserved. When the session ended, the state was lost.

**What it revealed:** The system had no auto-restart capability. There was no heartbeat monitor. There was no mechanism to detect that an agent had gone silent and alert the team. There was no way for a new session to automatically load the context needed to resume from where the previous session left off. The system was entirely dependent on humans noticing the outage and manually re-engaging.

**What changed:** Sprint 3 introduced three critical reliability capabilities. First, WF-AI-001 — the auto-restart workflow running on a 60-second heartbeat check. If no agent records activity, the workflow re-queues the last known active directive and sends a Telegram alert to Buck. Second, the Unified Operational State Model — a structured JSON document in the repository that any agent can read on session start to immediately understand the current state of all directives, projects, and system configuration. Third, the idle monitor (AUTO-IDLE-001) — a 30-minute timeout that triggers a check of Telegram channels and sends a message prompting the team to resume if no activity has been recorded.

**The principle established:** Operational continuity cannot rely on humans noticing outages. The system must detect its own failures and alert the responsible party. Every agent must be able to come online cold and immediately understand what work is in progress.

---

### Lesson 3: Long Messages Get Truncated

**What happened:** During early GBT directive cycles, the Operations Intelligence agent (Browser Claude) composed long, detailed directive messages to the Chief Architect. GBT received only the message title, not the body. Instructions were missed. Work was not executed.

**What it revealed:** The ChatGPT interface has message length constraints that are not visible to the sender. Messages that appear complete in the compose window are silently truncated in delivery. The receiving agent has no way to know the message was truncated — it simply sees less content.

**What changed:** All GBT directives are now structured as short, focused messages. When a directive requires substantial context, it is broken into numbered parts (Part 1 of 2, Part 2 of 2). Each part is self-contained. The receiving agent acknowledges each part before the next is sent.

**The principle established:** Communication architecture must account for platform constraints. Never assume a message was received as composed. Keep messages short. Use multi-part structure for complex instructions. Verify receipt.

---

### Lesson 4: The One-Source-of-Truth Discipline

**What happened:** Early in the build, information about the same subject existed in multiple places: sprint state was in GitHub, in Telegram messages, and in agent context. When these sources diverged, agents made decisions based on stale information. Work was duplicated. Decisions were reversed.

**What it revealed:** Multiple sources of truth create coordination problems that compound over time. Each agent that reads from a different source creates a consistency gap. The gaps accumulate until an inconsistency becomes a production error.

**What changed:** The GitHub repository became the single authoritative source of truth for all operational state. The CURRENT_SPRINT.md file is the authoritative sprint record. AI_TEAM/ documents are the authoritative architecture and governance records. Every agent reads from GitHub at session start and writes to GitHub at session end. Telegram and direct agent communication are for real-time coordination only — they are not the record.

**The principle established:** Every piece of operational data must live in exactly one place. That place must be durable, version-controlled, and accessible to all agents. GitHub satisfies all three requirements.

---

### Lesson 5: Audit Before Building

**What happened:** In Sprint 2, development work on new capabilities revealed that some of the capabilities being built already existed in a different form. Time was spent implementing features that were already partially implemented elsewhere. The duplication created maintenance problems.

**What it revealed:** Without a systematic audit before each sprint, the team does not have a reliable inventory of what already exists. New work gets created without checking whether existing work can be extended. Duplication becomes a structural problem.

**What changed:** The audit-before-building principle became a mandatory first step for every sprint. Sprint 3 began with a comprehensive audit of all existing capabilities, all committed documents, all gateway endpoints, and all n8n workflows. The audit results were committed as CONSTRUCTION_OS_COMPLETENESS_AUDIT.md before any new Sprint 3 development began.

**The principle established:** Never build before auditing. The cost of discovering duplication after development is far higher than the cost of auditing before. A 30-minute audit at the start of a sprint can save days of rework.

---

### Lesson 6: Governance Through Telegram

**What happened:** During a period when Buck was away from his desktop, governance decisions in the Approval Queue waited. Items expired. Work that required authorization stalled. The team had no way to reach Buck through the system — only through external communication channels.

**What it revealed:** Governance that requires desktop access is not operational governance. Construction business moves on job sites, in vehicles, and on phones. If Buck cannot make governance decisions from his phone, the governance system becomes a bottleneck.

**What changed:** Telegram-based governance was elevated to a primary Sprint 3 workstream. The Telegram bot will allow Buck to approve, reject, escalate, and authorize directly from his phone. The TELEGRAM_AUTH_SPEC.md and TELEGRAM_ARCHITECTURE_SPEC.md documents define the complete implementation. No approval should ever require a laptop.

**The principle established:** Governance must be accessible wherever the executive is. Mobile-first approval is not a convenience feature — it is an operational requirement.

---

### Lesson 7: The System Must Know It Is Idle

**What happened:** Between operational sessions, the system sat idle without any awareness that time was passing and work was waiting. Buck would return to find that nothing had progressed. The system had no voice of its own — it could not reach out and say "We are idle. Should we resume?"

**What it revealed:** A purely reactive system — one that only works when prompted — is not an operating system. An operating system has its own continuity. It knows its own state. When it detects that it has been idle, it acts.

**What changed:** The IDLE_MONITOR_SPEC.md established AUTO-IDLE-001: if no agent records activity for 30 minutes, the system sends a Telegram message to Buck prompting the team to resume, checks the Telegram channels for any pending messages, and re-queues the last known directive. The system does not wait to be told to work.

**The principle established:** An operating system has its own operational continuity. It detects its own idle state and takes appropriate action. Build systems that know when they are not working and have a defined protocol for restarting themselves.

---

### Lesson 8: The Chief Architect Is the Strategic Partner

**What happened:** In early operating cycles, the Operations Intelligence agent (Browser Claude) attempted to make all architectural decisions independently — designing systems, specifying implementations, and committing architecture documents without GBT review.

**What it revealed:** Browser Claude is an excellent execution coordinator but is not the right tool for architectural design. GBT — the designated Chief Architect — brings a more systematic architectural perspective and produces better-structured specifications when given the right directives.

**What changed:** The collaboration model was established. Browser Claude fires directives to GBT at the end of every operational cycle. GBT designs architecture. Browser Claude captures GBT’s response and commits it to the repository. The cycle repeats. Every major architectural document in the AI_TEAM/ folder was designed by GBT and captured by Browser Claude through this process.

**The principle established:** Use the right agent for the right task. Architect with the architect. Implement with the implementer. Coordinate with the coordinator. Collaboration is not optional — it is what makes the system stronger than any individual agent.

---

### The Defining Characteristic of a Mature System

A mature engineering organization does not hide its mistakes. It learns from them, documents them, and uses them to build a better system for everyone who follows.

Every incident in this chapter made the HCI AI OS more resilient, more trustworthy, and more capable. The email incident tightened governance. The shutdown built auto-restart. The truncation problem changed communication architecture. The one-source-of-truth discipline created consistency. The audit-before-building rule prevented duplication. The Telegram governance requirement made approval mobile. The idle monitor gave the system its own voice.

Each lesson is permanent. The knowledge does not reset when a session ends. It lives in the architecture, in the code, in the governance documents, and in this manual.

That is what it means to build a learning organization.

---

*Chapter expanded by Browser Claude | Historical audit from Sprint 1 through Sprint 3 | 2026-07-01*


---
## Chapter 12 — The Future of HCI

### The Company We Are Building

Every company eventually reaches a point where technology is no longer the competitive advantage.

The competitive advantage becomes the organization itself.

The HCI AI Operating System is not intended to make Hendrickson Construction a company that uses artificial intelligence. It is intended to make Hendrickson Construction a company whose organizational intelligence — accumulated across every project, every relationship, every decision — becomes a durable competitive asset that grows stronger every year.

---

### When the System Is Fully Mature

Imagine the HCI AI Operating System operating at full maturity.

**The Estimator**

An estimator walks a site for the first time.

Before the visit is complete, the operating system has already pulled comparable projects from the company's history, surfaced relevant vendor pricing from the last three years, identified trades that historically perform well in this building type and neighborhood, and generated a preliminary budget range based on actual HCI experience rather than industry averages.

The estimator does not start from scratch. The estimator starts from everything the company already knows.

**The Project Manager**

A Project Manager opens a new project for the first time.

The operating system has already reviewed the drawings, identified the highest-risk specifications, flagged the long-lead items that have caused delays on similar projects, and mapped the subcontractor relationships most relevant to this scope.

Before the first meeting, the PM already knows where to look.

When an RFI arrives from the architect, the system immediately surfaces every similar RFI from past projects, the responses that worked, and the downstream effects that followed. The PM spends their time making decisions rather than researching history.

**The Superintendent**

The Superintendent arrives on site.

The field dashboard already knows: today's inspections, deliveries, weather impacts, subcontractors on site, critical installations, and unresolved field questions.

When an unexpected condition is discovered, the system immediately identifies similar situations from previous projects and surfaces the resolutions that proved successful. The Superintendent remains responsible for the decision. The operating system ensures they never begin with an empty page.

**Buck**

Buck wakes up.

Mission Control has already reviewed overnight activity across every active project. The morning brief is waiting — not a generic status report, but a prioritized list of what needs Buck's attention today, what can proceed without input, and what has already been handled by the team.

The company has been running for hours before the first call of the morning.

Buck's time is spent on leadership, relationships, strategy, and the decisions that require judgment. The operating system handles everything that can be handled without it.

---

### The Vendor Network

Every subcontractor relationship becomes part of a living body of knowledge.

Over time, the operating system understands which vendors consistently deliver on schedule, which trades require more lead time than their contracts suggest, which contractors perform best on occupied renovations versus ground-up work, and which relationships have compounded in value across multiple projects.

Procurement decisions stop being educated guesses. They become evidence-based recommendations built from the company's actual experience with actual contractors on actual projects in actual conditions.

A new vendor is evaluated not just on their current bid but on how similar vendors have performed. A returning vendor arrives with their complete performance history already loaded.

The vendor network becomes one of HCI's most valuable and least replicable assets — because it can only be built through the accumulated experience of doing the work.

---

### Predictive Intelligence

The gap between construction intelligence and construction reality closes.

Today, problems are identified when they appear. In a mature HCI AI Operating System, problems are identified before they arrive.

Schedule risks surface when procurement falls behind, not when activities slip. Budget exposure appears when change order patterns match historical precedents, not when costs are already committed. Inspection readiness is tracked continuously, not assembled the week before the walk-through.

The team spends less time reacting and more time preventing.

---

### The Organization Compounds

The most important feature of the HCI AI Operating System is not any individual capability.

It is that the system compounds.

Every completed project adds to the estimating intelligence. Every closed RFI adds to the response library. Every resolved field condition adds to the knowledge base. Every approved change order adds to the cost intelligence. Every vendor evaluation adds to the procurement database.

A company that has been operating HCI AI OS for five years knows things that no competitor can replicate from a standing start. The knowledge is not in a document. It is embedded in the operational fabric of the company.

New employees contribute to it from day one. Experienced team members draw from it every day. The system ensures that when someone leaves, their knowledge does not leave with them.

---

### Expanding Capability

As the platform matures, its capabilities expand in proportion to the trust the team places in it.

The first phase was building the foundation: reliable data, governed workflows, durable architecture.

The second phase is operational intelligence: predictive risk, compounding vendor knowledge, automated coordination.

The third phase is organizational intelligence: a platform that allows Hendrickson Construction to take on more work, serve clients better, and operate with the confidence that comes from knowing the company's accumulated experience is always available and always growing.

The team does not get smaller. It gets more capable.

---

### Continuous Learning

The operating system never graduates.

Every completed project improves: estimating, scheduling, procurement, coordination, communication, documentation, and governance.

Improvement is no longer an annual initiative. It becomes part of daily operations. Every project leaves the company stronger than it found it.

---

### Building the Best Construction Company We Can

People will not remember the software.

They may remember the dashboards. They may remember the AI.

But those are not the true legacy of the HCI AI Operating System.

The legacy is a company that chose to preserve its knowledge, strengthen its governance, and invest in a way of working that becomes more capable with every project completed.

Buildings will continue to rise from concrete, steel, wood, and glass.

Hendrickson Construction will continue to be built from something less visible but ever more valuable: disciplined people, trusted relationships, hard-earned experience, and a shared operating system that ensures none of those assets are ever lost.

That is the future of HCI — not simply a company that uses AI, but a company whose collective intelligence grows every day, making each project safer, smarter, more predictable, and more successful than the last.


### The Next Generation of Tools

The HCI AI Operating System is architected to integrate new capabilities as they become available and proven. The following tools represent the next generation of additions under active evaluation.

**Perplexity AI — Real-Time Research Intelligence.** Construction decisions require current market information: today's lumber prices, current lead times on mechanical equipment, the reputation of a subcontractor who just submitted a bid. Training data cutoffs mean that AI systems without web access cannot provide reliable answers to these questions. Perplexity AI brings real-time web search capability to the operating system. Use cases include: material cost benchmarking against current market rates, building code and energy code research for specific jurisdictions, subcontractor reputation research from online sources, manufacturer lead time verification, and competitive intelligence on project opportunities. Perplexity integrates as a research service layer that any AI agent can call when current-market information is required.

**AI Plan Reader — Construction Document Intelligence.** The ability to read, interpret, and extract structured data from architectural and engineering drawings represents one of the highest-value opportunities in AI-integrated construction. Phase 1 deploys PDF parsing (PyMuPDF or pdfplumber) to extract keynotes, specifications cross-references, room schedules, door and window schedules, and equipment lists from drawing sets. Phase 2 adds computer vision analysis using a vision-capable AI model to identify elements not captured in text — structural grids, equipment layouts, accessibility paths, and site features. Phase 3 integrates Bluebeam or Procore APIs to pull live drawing sets directly into the operating system. Goal: the AI system reads the full drawing set on bid day and produces a structured scope extraction in hours, not days.

**Critical Path Method (CPM) Scheduling Engine.** Current scheduling relies on manual superintendent input and PM oversight. The CPM engine adds a full network-aware scheduling layer in PostgreSQL. Every project activity has defined predecessors, successors, durations, and resource assignments. The engine calculates float, identifies the critical path, and updates automatically as field reports are received. When a critical path activity falls behind, the system alerts immediately — not at the end of the month when the schedule update is submitted.

**Cost Forecasting — Earned Value Management.** A real-time cost-to-complete forecast that runs continuously as the project executes. Inputs include: original budget, committed costs, actual costs to date, earned value percentage by trade, and remaining scope based on the current schedule. Output is a projected final cost, projected variance, and a confidence interval. Alerts fire when any trade exceeds threshold variance. Buck sees the financial trajectory of every project, every week, without waiting for a monthly report.

**Subcontractor Portal.** A secure, simple web interface where subcontractors submit structured bids, acknowledge purchase orders, confirm delivery commitments, and submit lien waivers. The portal eliminates email chains for routine procurement communications and creates a structured record of every sub interaction.

**Photo AI and Field Documentation.** Superintendents photograph work in place. The AI system compares the photograph to the approved drawings, identifies work completed versus work remaining, flags potential safety concerns, and attaches a structured observation record to the Project Brain. Progress photography becomes operational data.

---

### What HCI Looks Like in Five Years

In five years, a Hendrickson Construction project operates like this:

A bid invitation arrives. The AI system immediately retrieves comparable project history, generates a preliminary scope matrix from the project description, and assembles a list of qualified subcontractors from the vendor database with their performance history. By the time the estimator sits down to review the opportunity, they have two hours of research already completed.

The estimator walks the site with a phone. Photos are automatically analyzed. Field observations are dictated and transcribed. The scope matrix is populated in real time. By the end of the site visit, the estimate is 60% complete.

The bid is prepared and submitted. The system tracks the outcome. If HCI wins, the project is initialized in five minutes: Project Brain created, schedule loaded, budget distributed, subcontractor bid packages assembled. The superintendent receives a digital briefing before the first day on site.

During construction, the project runs on its own rhythm. Field reports arrive each morning from the superintendent, recorded in under 10 minutes. The AI system processes each report: updating the schedule, flagging variance, drafting client updates, and identifying risks before they become problems. The PM reviews the exception report — not the raw data.

When the project closes, every piece of data — costs, schedule, vendor performance, lessons learned — is captured automatically in the organizational knowledge base. The next project starts smarter because this project ran.

That is not a technology story. It is an organizational capability story. And it is exactly what HCI AI OS is being built to enable.

---

### The Commitment

Building this future requires sustained commitment. Not to specific tools or specific vendors — those will change. The commitment is to the principles: one source of truth, human authority remains final, governance enables rather than blocks, the system learns continuously, and the team never stops improving.

Hendrickson Construction is not building this because it is fashionable. It is building this because the construction industry is changing, and the companies that build the operational infrastructure now will have capabilities in five years that their competitors cannot match regardless of how much money they spend later.

The infrastructure takes time to build correctly. That is why HCI is building it now.

---

*Chapter expanded by Browser Claude | Future capabilities section added from GBT Cycle 5 recommendations | 2026-07-01*


---
## Chapter 13 — Implementation Guide

### How to Build, Extend, and Maintain the HCI AI Operating System

The HCI AI Operating System is designed to outlive individual developers, AI models, and software frameworks.

This chapter exists for the people who will inherit the system.

Some will be software developers.

Some will be project managers.

Some will be future AI agents.

Some may not yet exist.

The objective is simple:

Leave the operating system better than you found it.

Every enhancement should improve the platform without increasing unnecessary complexity.

The operating system is successful when future contributors extend it naturally rather than rebuilding it.

**The First Rule**

Before writing code:

Read the current state.

Never begin implementation from memory.

Always begin from operational truth.

Review:

- Mission Control
- LIVE_PROJECT_STATE
- CURRENT_SPRINT
- Architecture Decision Records
- Open implementation directives
- Approval Queue
- Recent Architecture Review Board decisions

Then build.

---

### 1. Adding a New Workflow

A workflow is a repeatable automated process that executes a business function.

Before adding one, confirm it does not already exist.

Search the n8n workflow registry.

Search the Python workflow directory.

If a workflow already exists, extend it.

**Step 1 — Define the Business Function**

A workflow exists because a business function requires it.

Document:

- What business process does this automate?
- What SOP governs it?
- What approvals does it require?
- What data does it read?
- What data does it write?
- Who is the operational owner?

No implementation begins without a documented business function.

**Step 2 — Follow Naming Conventions**

Workflow names should be descriptive and stable.

Examples:

- WF-003 Morning Brief
- WF-012 Daily Field Report
- WF-021 Bid Comparison
- WF-034 Vendor Intelligence Refresh

Avoid names based on implementation details.

Prefer names based on business function.

**Step 3 — Link to an SOP**

Every production workflow should reference its governing Standard Operating Procedure.

The workflow should answer:

- Why does it exist?
- What business process does it implement?
- What approvals apply?
- What evidence is retained?

Automation without documentation becomes operational debt.

**Step 4 — Register in n8n**

For automated workflows:

1. Create a new workflow in n8n at localhost:5678
2. Name it using the WF-NNN convention
3. Add a trigger: webhook, schedule, or event
4. Wire data transformations in the node sequence
5. Add approval gates where writes occur
6. Add error handling on every node that touches production data
7. Test against staging data before activating

**Step 5 — Expose via Gateway (if AI-accessible)**

If the workflow should be callable by AI agents:

1. Add an endpoint to the FastAPI router at api/routers/
2. Register the capability in the GBT gateway OpenAPI spec
3. Document the request and response schema
4. Add authentication enforcement
5. Wire to the workflow trigger via HTTP or direct function call
6. Test the end-to-end path from GBT gateway to FastAPI to n8n to result

**Step 6 — Validate Against the Testing Gate**

The system requires 48/48 tests to pass before any workflow is considered production-ready.

Run the full test suite:

- Unit test the workflow logic
- Integration test the data paths
- Smoke test the gateway call
- Verify the approval gate blocks writes without authorization

Add the new workflow to the test matrix.

The gate does not pass until the new workflow is covered.

---

### 2. Extending the GBT Gateway

The Gateway is the public interface to the operating system.

Treat it as a product.

**Step 1 — Determine Whether an Endpoint Already Exists**

Search first.

Never duplicate existing capability.

Questions:

- Does another endpoint already solve this?
- Can an existing endpoint be extended?
- Is the business object already represented?

Prefer extension over creation.

**Step 2 — Write the OpenAPI Spec Entry**

The gateway spec lives at: 03_Source_Code/api/routers/gbt_gateway.py

Add:

- A clear operation summary
- Request body schema with field descriptions
- Response schema with field descriptions
- Authentication requirement
- Error response documentation

The spec is the contract.

Implementation should match the spec exactly.

**Step 3 — Wire to the FastAPI Router**

Add the handler function.

The handler should:

- Validate the request
- Authenticate the caller
- Route to the appropriate service or workflow
- Return a structured response
- Log the operation to the audit trail

Testing should prove that implementation matches the documented contract.

---

### 3. Adding a New Construction Project

Projects should enter the operating system consistently.

Every project follows the same initialization sequence.

**Step 1 — Create Project State**

Create the Project State record.

Include:

- project identifier
- client
- address
- owner
- phase
- budget
- schedule
- health
- active sprint
- responsible personnel

This becomes the canonical project identity.

**Step 2 — Initialize the Approval Queue**

Every project requires its own approval queue entries.

No writes occur without approval queue enforcement.

Confirm:

- The project identifier is registered
- All write operations route through the queue
- Buck Adams is the authorizing approver for all entries
- The queue is visible in Mission Control

**Step 3 — Link to the Morning Brief**

The morning brief runs daily.

Add the new project to the morning brief configuration so Buck receives daily status.

Confirm the project appears in:

- morning brief output
- project health dashboard
- approval queue summary

**Step 4 — Validate Data Integrity**

Before the project enters production:

- Confirm all required fields are populated
- Confirm no test data remains in production records
- Confirm schedule items reflect real dates
- Confirm risk counts are accurate
- Confirm bid packages reflect real procurement status

Data integrity is confirmed before the project is considered live.

---

### 4. Onboarding a New AI Agent

New AI participants should be treated as new team members.

Capabilities should be explicit.

Responsibilities should be limited.

Authority should be documented.

**Step 1 — Define the Role**

Document:

- responsibilities
- authority
- limitations
- operational owner

Avoid overlapping responsibilities whenever practical.

**Step 2 — Write the Capability File**

Every AI agent requires a capability file in AI_TEAM/.

The file documents:

- What the agent can do
- What the agent cannot do
- What approvals the agent requires
- What data sources the agent can access
- What actions require human review

Future operators should never guess what an AI participant is allowed to do.

**Step 3 — Establish the Inbox/Outbox Pattern**

The agent receives work through directives.

The agent delivers results through commits or gateway responses.

Directives are written by Browser Claude and approved by GBT before dispatch.

Results are committed to the repository.

No agent should communicate operational decisions directly to external parties without human approval.

**Step 4 — Require ARB Review**

Before the agent operates in production, the Architecture Review Board approves:

- the agent's capability scope
- the agent's authority limits
- the integration points
- the failure modes and fallbacks

The Architecture Review Board approves structural changes to the AI organization.

**Step 5 — Capability Documentation**

Document:

- supported operations
- prohibited operations
- approval requirements
- known limitations
- integration points

Future operators should never guess what an AI participant is allowed to do.

---

### 5. Running a System Audit

The Browser Claude audit process should become institutional practice.

Every significant review should follow the same sequence.

**Step 1 — Review Repository Activity**

Inspect:

- recent commits
- open directives
- pending inbox items
- unresolved blockers

The repository is the source of truth.

**Step 2 — Review Email Paths**

Verify:

- all email send paths are accounted for
- no unauthorized sends have occurred
- draft-only enforcement is active
- approval queue is enforcing authorization before delivery

Email governance is non-negotiable.

**Step 3 — Review Live Data vs. Test Data**

Confirm:

- production records contain real field data
- no test seeds remain in live tables
- superintendent names reflect actual personnel
- risk counts are accurate
- schedule items reflect real dates

Test data in production causes operational errors.

**Step 4 — Review Sprint State**

Confirm:

- LIVE_PROJECT_STATE is current
- CURRENT_SPRINT reflects active work
- completed items are closed
- open items have owners and timelines

Sprint state should reflect operational reality.

**Step 5 — Fire a Verification Directive**

Dispatch a structured directive to Claude Code.

The directive should:

- list open items requiring resolution
- specify the expected output format
- require a commit confirming completion
- include a deadline

Directives without completion criteria are advisory.

Directives with completion criteria are operational.

**Step 6 — Review Mission Control**

Confirm:

- project health
- AI health
- approvals
- directives
- risks
- system status

Mission Control should accurately represent operational state.

**Step 7 — Review Governance**

Verify:

- approval enforcement
- audit logging
- authorization
- documentation

Governance should be visible.

**Step 8 — Document Findings**

Every audit produces a findings document.

The document includes:

- what was audited
- what was found
- what was corrected
- what remains open
- who is responsible for open items

Findings without documentation do not exist.

**Step 9 — Report to Buck**

Every audit concludes with a direct report to Buck Adams.

The report should be brief, specific, and actionable.

Buck makes final decisions on open items.

---

### 6. System Health Checklist

**Daily**

- Morning brief delivered to Buck
- Approval queue reviewed
- Project health: green/yellow/red for all active projects
- AI agent status: all agents operational or documented as offline
- Open directives: acknowledged and assigned
- Email paths: no unauthorized sends in the last 24 hours

**Weekly**

- Sprint state reviewed and updated
- Architecture Decision Records updated
- Repository commits reviewed for consistency
- Vendor intelligence updated
- Field data accuracy confirmed
- Review Mission Control dashboard against live system state
- Vendor intelligence updates
- Workflow health inspection
- Backup success confirmed
- Approval history reviewed
- Recurring incidents documented
- Opportunities to simplify the system identified

Weekly reviews focus on trends rather than individual events.

**Sprint Close Checklist**

A sprint should close only after confirming:

- implementation complete
- testing complete
- documentation updated
- governance verified
- Architecture Review Board approval recorded
- Mission Control synchronized
- repository consistent
- production state validated
- outstanding risks assigned

Code completion alone does not end a sprint.

Operational readiness does.

---

**Closing Principle**

The HCI AI Operating System is a living platform.

It will grow as HCI grows.

It will adapt as construction practice evolves.

It will incorporate new tools, new AI models, and new integrations.

The principles that should not change:

- Governance before automation
- Audit before build
- Documentation as implementation
- Human authority over consequential decisions
- Every system earns the trust placed in it

AI models will change.

Construction methods will evolve.

The principles behind the HCI AI Operating System should remain stable.

Protect the source of truth.

Preserve governance.

Document decisions.

Prefer simplicity.

Build systems that survive restarts, personnel changes, and years of continuous operation.

If future developers, future project managers, and future AI agents can inherit the platform and confidently extend it without first untangling it, then the implementation guide has fulfilled its purpose.

That is the standard to which every contributor should hold themselves—and the standard by which the HCI AI Operating System should continue to evolve.

---

## Chapter 14 — Superintendent Operations

### The Field Intelligence Layer

The HCI AI Operating System does not manage construction.

Superintendents manage construction.

The operating system manages information.

This distinction matters.

The system exists to make information available when it is needed, in a form that is useful, without requiring the Superintendent to produce it manually.

This chapter explains how the system supports field operations and what Superintendents need to know to use it effectively.

---

### 1. The Superintendent Daily Dashboard

The Superintendent Daily Dashboard is the field view of the operating system.

It is designed to give the Superintendent a complete picture of the day before the day begins.

**What the Dashboard Shows**

**Schedule**

The dashboard shows:

- today's planned activities
- activities that are behind schedule
- critical path items
- items that are at risk of delay

Schedule information comes from the project schedule linked to the operating system.

**Crew**

The dashboard shows:

- crews expected on site today
- trade assignments
- any reported crew shortages

**Materials**

The dashboard shows current status for:

- Concrete
- Steel
- Framing
- Electrical
- Plumbing
- HVAC
- Fire Protection
- Drywall
- Finishes

Unexpected shortages are highlighted automatically.

**Deliveries**

The dashboard lists:

- expected deliveries
- delayed deliveries
- missing materials
- long-lead items
- items requiring inspection before installation

Material problems are easier to solve before crews begin waiting.

**Safety**

Safety appears near the top because it always comes first.

The dashboard highlights:

- open safety items
- required inspections
- safety observations from previous logs
- any items escalated to the Project Manager

**How to Read It**

Green means the project is moving.

Yellow means the project needs attention.

Red means the project requires immediate decision.

The Superintendent decides.

---

### 2. Daily Field Logs

The Daily Field Log is one of the most valuable documents created during construction.

It is more than a daily report.

It becomes permanent project memory.

**Complete It Every Day**

A complete field log should include:

**Weather**

- temperature
- precipitation
- wind
- unusual conditions

Weather explains many schedule decisions.

**Workforce**

Record:

- trades on site
- head count per trade
- hours worked
- any crew changes or absences

**Work Completed**

Describe what was accomplished today.

Be specific.

Specific logs are useful in disputes.

Vague logs are not.

**Delays and Issues**

Document:

- any work that did not proceed as planned
- the reason
- what was done about it

The system does not judge delays.

The system records them so patterns become visible.

**Safety Observations**

Record every safety observation, positive or negative.

The system uses safety observations to identify recurring issues and sites that require follow-up.

**Quality Observations**

Record quality observations when work does not meet standard.

The system links quality observations to specific activities and generates follow-up items.

**Photos**

Photographs should tell the story of the day.

Capture:

- completed work
- concealed conditions
- safety observations
- quality concerns
- unexpected discoveries

Every photograph should have context.

**What the AI Does with Your Daily Log**

Once submitted, the operating system immediately begins organizing information.

It:

- indexes photographs
- links work to schedule activities
- updates Project Brain
- identifies recurring issues
- compares progress with schedule
- identifies possible risks
- prepares executive summaries

The Superintendent submits the log.

The system does the filing.

---

### 3. Schedule Variance and Health Indicators

The operating system monitors schedule continuously.

When variance is detected, it updates the project health indicator.

**Green**

Green means:

The project is on track.

Schedule variance is within acceptable tolerance.

No immediate action is required.

**Yellow**

Yellow means:

The project is drifting.

Possible causes:

- delayed procurement
- unresolved RFIs
- insufficient manpower
- inspection backlog
- weather impacts

Yellow is not failure.

Yellow means: Act now while options still exist.

**Red**

Red means:

Critical project objectives are at risk.

Examples:

- critical path slipping
- major procurement delay
- regulatory hold
- safety incident requiring investigation

Red triggers automatic notification to the Project Manager and Buck Adams.

**What the Superintendent Does with a Yellow or Red**

Assess the situation.

Identify the cause.

Determine corrective action.

Report to the Project Manager.

The operating system surfaces the variance.

The Superintendent resolves it.

---

### 4. RFIs and Submittals

RFIs and submittals are the paper trail of construction.

The operating system tracks them.

**RFIs**

When a field question requires a formal response:

1. The Superintendent documents the question and the condition
2. The Project Manager initiates the RFI
3. GBT (the HCI Chief Architect AI) drafts the RFI language
4. The Project Manager reviews and approves the draft
5. The RFI is submitted to the design team
6. The operating system tracks status until response is received

The AI drafts.

The human approves.

The response goes on record.

**Submittals**

The operating system tracks:

- required submittals
- current status
- pending approvals
- overdue reviews

If a required submittal threatens the schedule, both the Superintendent and Project Manager receive advance notice.

---

### 5. Safety and Quality Flags

Safety and quality are never secondary priorities.

They are operational priorities.

**Safety Escalation**

The system automatically escalates situations such as:

- repeated safety observations
- unresolved hazards
- missing required inspections
- repeated violations
- incidents requiring investigation

Automatic escalation does not replace reporting.

It ensures nothing is missed.

**Quality Escalation**

The system escalates quality issues when:

- the same issue is observed more than once
- work fails inspection
- a critical hold point is reached
- corrective work is required

Escalation generates a notification to the Project Manager.

The Project Manager determines whether to involve Buck Adams.

**What the Superintendent Does When Something is Flagged**

Investigate.

Document.

Correct.

Report.

The system supports the process.

The Superintendent owns the outcome.

---

### 6. What Buck Sees Every Morning

Every morning, Buck Adams receives a morning brief.

The morning brief is a cross-project summary.

It reflects the data submitted the previous day.

**The Morning Brief Includes**

- Project health summary for all active projects
- Schedule variance flags
- Open approvals requiring Buck's decision
- Safety flags
- Active risks
- Procurement status
- AI system status

**How Field Data Shapes the Brief**

Every daily field log influences the morning brief.

If a Superintendent documents a delay, that delay appears in the brief.

If a Superintendent documents a safety observation, it appears in the brief.

If a Superintendent documents a quality issue, it appears in the brief.

The brief is only as accurate as the logs.

Accurate logs produce accurate briefs.

Accurate briefs support better decisions.

---

### 7. What Superintendents Do vs. What the AI Handles

**The Superintendent**

Responsible for:

- leading crews
- coordinating trades
- observing work
- documenting conditions
- identifying issues
- protecting safety
- maintaining quality
- making field decisions
- communicating with the Project Manager

Leadership remains human.

**The AI Operating System**

Responsible for:

- organizing information
- indexing photographs
- linking documents
- tracking RFIs
- monitoring schedule variance
- monitoring procurement
- identifying trends
- preparing draft reports
- highlighting risks
- updating the Project Brain
- preparing the morning brief

The AI does not manage people.

The AI does not make field decisions.

The AI does not replace the Superintendent's judgment.

**Working Together**

The system works best when Superintendents use it consistently.

Log every day.

Be specific.

Document what happened, not just what was planned.

The system learns from consistent input.

Consistent input produces useful output.

Use the same formats whenever practical.

Consistency produces better projects.

**The Goal**

The HCI AI Operating System is not intended to place another screen between the Superintendent and the work.

Its purpose is exactly the opposite.

By reducing administrative effort, organizing project information automatically, and surfacing issues before they become crises, the operating system gives Superintendents more time to do what only they can do: lead people, coordinate construction, maintain quality, protect safety, and keep the project moving forward.

When the system is working properly, it quietly handles the information while the Superintendent focuses on building the project. That is the Field Intelligence Layer—technology in service of construction, not construction in service of technology.

---

## Chapter 15 — Project Manager Operations

### The Intelligence Layer

The Project Manager is the operational center of every project.

The Superintendent leads the field.

The Estimator manages procurement.

The Owner provides direction.

The Project Manager connects them all.

The HCI AI Operating System is designed to reduce the time spent gathering information so more time can be spent making decisions, solving problems, and serving clients.

This chapter explains how Project Managers use the operating system to run projects—not software.

---

### 1. The PM View of Mission Control

Mission Control is the PM's command center.

It synthesizes information from across the project into a single operational view.

**Project Health**

Every project displays a health indicator.

Typical indicators include:

- Green
- Yellow
- Red

Health is determined by multiple factors working together, including:

- schedule
- procurement
- RFIs
- submittals
- approvals
- safety
- quality
- client commitments

Health is not a score.

It is a conversation starter.

**Schedule**

Mission Control immediately highlights:

- activities behind schedule
- critical path movement
- milestone risk
- pending approvals blocking schedule

**Risks**

The operating system flags:

- open risks
- unresolved issues
- trends requiring PM attention

Examples include:

- delayed procurement
- repeated quality issues
- inspection bottlenecks
- vendor performance decline
- schedule compression
- unresolved design conflicts

These are recommendations for attention.

They are not conclusions.

**Approvals**

Mission Control highlights:

- approvals waiting for PM action
- approvals waiting for Buck
- recently completed approvals
- overdue approvals

Approvals should never disappear into email.

**Acting on Mission Control**

The dashboard exists to prioritize your day.

A well-functioning project requires the PM to act on what Mission Control surfaces.

If Mission Control is ignored, it stops being useful.

---

### 2. The Weekly PM Review

The weekly review is the PM's primary reporting cycle.

The operating system generates the review automatically.

**What It Pulls**

The weekly PM review synthesizes:

- all daily field logs from the previous week
- schedule variance compared to baseline
- open RFIs and submittals
- approval queue activity
- risk register changes
- vendor activity
- safety and quality observations

**What Questions It Answers**

- Did the project move forward this week?
- What delayed progress?
- What decisions are required?
- What risks are growing?
- What does the client need to know?
- What executive decisions are required?
- What changed since last week?

If these questions cannot be answered quickly, improve the project's information quality.

**Presenting to Buck**

Executive reviews should emphasize decisions.

Not raw data.

Structure every update as:

Current Status: Where the project stands today.

Major Progress: What improved since the last review.

Risks: What could affect project success.

Decisions Needed: What Buck must decide.

The operating system prepares the data.

The PM prepares the interpretation.

---

### 3. Managing the Approval Queue

The Approval Queue is the gateway between AI-generated work and production action.

Nothing consequential happens without approval.

**What Goes Into the Queue**

- vendor write updates
- bid awards
- RFI submissions
- subcontract changes
- document distributions
- any system-generated action with external consequence

**What the PM Approves**

The PM approves operational items:

- RFI drafts
- submittal actions
- routine vendor communications
- bid follow-up reminders
- field coordination items

**What Requires Buck**

Anything with financial consequence.

Anything with client commitment.

Anything with contract implication.

Anything the PM is uncertain about.

When uncertain, escalate.

The queue exists because governance matters.

Nothing should skip the process.

---

### 4. Bid Management

Bid management is one of the operating system's most valuable capabilities.

The AI organizes information.

The Project Manager evaluates it.

**What the AI Does**

For each bid package, the operating system can:

- compare pricing
- identify exclusions
- summarize alternates
- highlight qualifications
- compare historical vendor performance
- identify unusual pricing
- detect missing scope
- monitor bid expiration

The operating system prepares the comparison.

**What the PM Does**

The PM:

- reviews the leveled comparison
- identifies scope gaps requiring clarification
- determines which vendors require follow-up
- makes the award recommendation
- submits the recommendation to Buck for approval

Award authority belongs to Buck.

Award preparation belongs to the PM.

---

### 5. RFI and Submittal Management

RFIs and submittals are construction's formal information exchange.

The operating system tracks every item from initiation to resolution.

**RFIs**

When a field question requires a formal response, the PM:

1. Receives the question from the Superintendent
2. Confirms the question is clear and complete
3. Reviews the AI-drafted RFI language from GBT
4. Approves or modifies the draft
5. Submits to the design team
6. Monitors status until response is received
7. Distributes the response to the field

The PM owns the RFI log.

The operating system maintains it.

**Submittals**

Monitor continuously:

- outstanding items
- overdue reviews
- rejected submissions
- critical-path materials
- procurement dependencies

The AI tracks progress.

The PM keeps work moving.

---

### 6. Communicating with Subcontractors

Communication should be accurate, timely, and documented.

The operating system assists without replacing professional responsibility.

**What the AI Drafts**

Examples include:

- meeting summaries
- procurement reminders
- bid invitation letters
- scope clarification requests
- schedule notices
- compliance reminders

**What the PM Reviews Before Sending**

Every AI-drafted communication requires PM review before distribution.

The PM confirms:

- the content is accurate
- the tone is appropriate
- the commitments match project reality
- no unauthorized promises have been made

**What Never Goes Without Buck's Approval**

- any communication implying contract change
- any communication with schedule or cost commitment
- any communication involving a dispute
- any communication to a party with whom HCI has a legal relationship

When uncertain: do not send. Escalate to Buck.

---

### 7. The PM's Relationship with the AI Team

The AI team serves the PM.

Not the other way around.

**Ask GBT When**

Strategic analysis is needed.

Examples include:

- reviewing contract language
- drafting RFIs or scope clarifications
- preparing bid comparisons
- developing risk responses
- analyzing historical cost data
- preparing executive summaries

GBT is your operational analyst and governance partner.

**Involve Claude Code When**

Implementation is required.

Examples include:

- workflow improvements
- software bugs
- automation changes
- integration work
- database improvements
- gateway enhancements

Claude Code builds the platform.

**Work with Browser Claude When**

Repository intelligence is needed.

Examples include:

- implementation verification
- documentation review
- repository audits
- duplicate detection
- directive management

**Call Buck When**

A decision requires Buck's authority.

Examples include:

- bid award
- scope change
- client commitment
- contract modification
- project go/no-go
- any situation where the PM is uncertain

Buck makes the decisions that matter.

The AI team prepares the information that supports those decisions.

**The Intelligence Layer**

The HCI AI Operating System does not make Project Managers obsolete.

It makes them more effective.

Instead of spending hours collecting information, Project Managers spend their time interpreting it, coordinating people, solving problems, and leading projects.

The operating system quietly handles the repetitive work of organizing documents, tracking commitments, monitoring schedules, preparing drafts, and preserving project history.

The Project Manager remains responsible for the project.

The operating system ensures that responsibility is supported by timely information, consistent governance, and the accumulated experience of every project Hendrickson Construction has ever completed.

That is the Intelligence Layer: a system that transforms information into operational awareness, allowing Project Managers to focus on the work that only experienced construction professionals can do.

---

## Chapter 16 — Estimator Operations

### The Bid Intelligence Layer

Estimating is one of the most influential disciplines within Hendrickson Construction.

The quality of an estimate affects every phase that follows.

A complete scope reduces change orders.

A well-managed procurement process improves schedules.

Strong vendor selection improves quality.

Accurate budgets improve client confidence.

The HCI AI Operating System exists to make estimators faster, more consistent, and better informed—not to replace professional judgment.

The operating system organizes information.

The Estimator evaluates risk.

---

### 1. How the AI Organizes Incoming Bids

Bid management begins before the first proposal arrives.

The operating system tracks each bid package from creation through award.

Instead of organizing this information manually, the operating system automatically associates each bid with its project and bid package.

**Bid Intake**

When a bid is received, the system records:

- Project
- Bid package
- Vendor
- CSI Division
- Date received
- Bid amount
- Alternates
- Qualifications
- Exclusions
- Expiration date
- Attached documents

The original proposal remains preserved.

Nothing is overwritten.

**Document Processing**

The operating system indexes each proposal so it can be retrieved, compared, and referenced later.

This indexing supports dispute resolution, lessons learned, and historical cost analysis.

---

### 2. Using the Bid Leveling Service

The Bid Leveling Service produces a standardized comparison across all proposals received for a single bid package.

**What It Produces**

The leveled comparison includes:

- Base bid amounts
- Alternate pricing
- Adjusted bid values
- Scope differences
- Missing scope
- Clarifications required
- Significant pricing deviations
- Recommendation notes

The output highlights differences that deserve human attention.

**Reading a Leveled Bid**

Do not focus only on price.

Review:

Scope: Did every bidder price the same work?

Exclusions: Which exclusions affect project risk?

Qualifications: Are assumptions reasonable?

Alternates: Are the alternates comparable across bidders?

Vendor history: What does the system know about each vendor's past performance?

The lowest number is not always the best answer.

**What GBT Analyzes**

GBT can provide analysis of bid comparisons including:

- scope gap identification
- risk flag commentary
- vendor performance summary
- award recommendation rationale
- historical price benchmarking

The Estimator reviews GBT's analysis before presenting to the Project Manager.

---

### 3. Vendor Intelligence

The operating system maintains a vendor intelligence profile for each subcontractor.

**What It Tracks**

The vendor profile includes:

- Company name and contact information
- Divisions of work
- Bid history
- Award history
- Contact information
- Project history

The profile grows as additional work is completed.

**Performance History**

Historical information may include:

- Bid responsiveness
- Award history
- Schedule performance
- Change order frequency
- Quality observations
- Warranty performance
- Safety performance
- Communication responsiveness

Performance is measured using observed project outcomes rather than anecdotal impressions.

**Reliability**

Reliability is not simply low price.

Reliable subcontractors consistently:

- submit complete proposals
- respond to correspondence
- perform on schedule
- communicate problems early
- stand behind their work

The operating system helps distinguish reliable vendors from unreliable ones using documented evidence rather than memory.

---

### 4. The Bid Package Workflow

The bid package workflow follows a defined sequence from scope definition to award recommendation.

**Step 1 — Define Scope**

Every bid package begins with a scope document.

The scope defines:

- what work is included
- what work is excluded
- what the subcontractor is responsible for
- what HCI provides
- schedule requirements
- quality standards

GBT can draft scope sections based on project drawings, specifications, and historical templates.

The Estimator reviews and approves all scope documents.

**Step 2 — Build the Bidder List**

The operating system suggests bidders based on:

- division of work
- prior HCI history
- geographic coverage
- vendor intelligence profile

The Estimator makes the final selection.

**Step 3 — Distribute**

Bid invitations are drafted by the system and reviewed by the Estimator before distribution.

Distribution is approved before any communication goes to vendors.

**Step 4 — Follow Up**

The system identifies vendors requiring follow-up based on:

- No response
- Missing proposal
- Incomplete submission
- Upcoming deadline

GBT can prepare reminder drafts.

The Estimator reviews communications before they are sent through approved company processes.

**Step 5 — Receive Bids**

Each proposal is captured, indexed, and linked to the bid package.

No manual filing should be required.

**Step 6 — Level Bids**

The Bid Leveling Service produces a standardized comparison.

**Step 7 — Award Recommendation**

The Estimator prepares an award recommendation based on:

- leveled comparison
- scope confirmation
- vendor intelligence
- budget position
- schedule requirements
- qualitative judgment

The recommendation goes to the Project Manager.

Award authority belongs to Buck Adams.

---

### 5. Budget Tracking

Budget integrity is a primary responsibility of the estimating function.

**ROM vs. Actual Bids vs. Bid Budget**

The operating system tracks three budget benchmarks:

ROM (Rough Order of Magnitude): Initial estimate before design development.

Bid Budget: Target procurement budget based on approved design.

Actual Proposals: Real market pricing from received bids.

Actual proposals provide real market pricing.

The operating system compares them against:

- ROM
- Current budget
- Historical pricing
- Similar projects

Variance becomes immediately visible.

**Variance Alerts**

Examples include:

- Bid exceeds budget by threshold
- Bid substantially below market expectation
- Significant spread between bidders
- Multiple missing scopes
- Budget erosion across multiple packages

Alerts identify areas requiring investigation—not automatic conclusions.

---

### 6. Buyout Decisions

Buyout is a business decision supported by evidence.

The Estimator's role is to organize that evidence clearly.

**What Goes to Buck**

Every buyout decision is presented to Buck Adams.

The presentation includes:

- recommended vendor
- bid comparison summary
- scope confirmation
- budget impact
- risk summary
- Estimator recommendation with rationale

**The Approval Gate**

No subcontract is awarded without Buck's approval.

The operating system routes award recommendations through the approval queue.

Buck reviews and approves or declines.

Declines require documented reason and a revised recommendation.

---

### 7. What the AI Handles vs. What Requires Estimator Judgment

**The AI Operating System**

The operating system can:

- Organize proposals
- Extract bid information
- Compare pricing
- Normalize formats
- Identify exclusions
- Highlight scope gaps
- Monitor bid expiration
- Track vendor responses
- Generate comparison tables
- Draft procurement summaries
- Preserve procurement history

These tasks reduce administrative effort.

**The Estimator Provides Judgment**

The Estimator decides:

- Whether scope is complete
- Which assumptions are acceptable
- Which risks matter
- Whether pricing is realistic
- Which subcontractor best fits the project
- What recommendation should be presented

Professional experience remains indispensable.

**The Bid Intelligence Layer**

The HCI AI Operating System transforms estimating from a document-management exercise into an intelligence-driven process.

Instead of spending valuable time collecting files, formatting spreadsheets, and tracking correspondence, Estimators spend their time evaluating scope, understanding risk, and making informed recommendations.

Every proposal contributes to organizational knowledge.

Every completed buyout strengthens vendor intelligence.

Every project improves the next estimate.

That is the purpose of the Bid Intelligence Layer: to combine the discipline of professional estimating with the speed, consistency, and institutional memory of the HCI AI Operating System, ensuring that every procurement decision is supported by evidence, governed by process, and informed by the experience of the entire company.

---

## Chapter 17 — Buck Adams Operating Guide

### Owner's Manual for the HCI AI Operating System

This operating system exists for one reason:

**To help you build a better Hendrickson Construction.**

It is not here to replace your judgment.

It is not here to automate leadership.

It is here to make sure that every morning begins with the best information the company can assemble, every important decision is supported by evidence, and every lesson learned becomes part of the company's future.

You remain in charge — as PM & Superintendent at Hendrickson Construction, and as owner of HCI-AI.

The operating system exists to multiply your effectiveness, not your workload.

---

### 1. What Buck Sees Every Morning

The morning brief arrives daily.

It is the operating system's single most important output.

**How to Read It**

The morning brief is an executive summary, not a project report.

It should begin with the company's overall condition.

**Company Health**

The first section should summarize the portfolio.

Examples include:

- Number of active projects
- Overall project health
- Critical risks
- Projects requiring executive attention
- AI system health
- Overnight implementation status

This is the executive dashboard, not a project report.

**Projects Requiring Attention**

Only projects that need executive awareness should appear here.

For each project, you should see:

- Current health
- Why it changed
- What decision may be required
- Recommended next action

The objective is to focus your attention where it has the most impact.

**Open Approvals**

This section lists everything waiting for your decision.

Each entry should show:

- What is being requested
- Why it needs your approval
- What happens if you approve
- What happens if you decline
- The submitting party

Your approval moves work forward.

Your decline stops it and triggers a revision.

**What to Act On**

After reading the morning brief:

1. Address any open approvals that are time-sensitive
2. Note projects moving from green to yellow or yellow to red
3. Follow up with the PM on projects requiring executive attention
4. Ask GBT for deeper analysis on anything that needs it

The morning brief should take fifteen minutes to read.

If it requires more than that, the brief needs to be improved.

---

### 2. The Approval Queue

The Approval Queue is where governed decisions wait for human authorization.

Think of it as the executive decision desk for the company.

It is not a task list.

It is not an inbox.

It is the authoritative record of decisions that require executive approval.

**What Belongs in the Queue**

Examples include:

- Contract awards
- Major financial commitments
- Significant client communications
- Governance exceptions
- Production actions reserved for executive approval

Routine operational work should not require your attention.

The queue should contain only decisions that genuinely benefit from executive review.

**How to Move Through It**

Review the queue in the morning brief.

For each item:

- Read the request summary
- Review the supporting evidence
- Approve or decline
- Add a note if the decision requires explanation

**What Happens Next**

Approved items:

The operating system executes the approved action.

Declined items:

The operating system returns the item to the submitting party with your decision recorded.

A revised recommendation may be submitted.

**Buck's Approval Rights Are Non-Delegable**

No one approves on your behalf.

The AI team does not approve.

The PM does not approve on your behalf.

Items in your queue wait until you review them.

---

### 3. Using GBT as Your Strategic Partner

GBT is the HCI Chief Architect.

It has access to the entire operating system.

It can synthesize information across every project simultaneously.

**What to Ask GBT**

Examples that work well:

- "Compare these bid packages."
- "Summarize the major changes since yesterday."
- "Draft an executive update for this client."
- "Show me the history of this subcontractor."
- "What projects resemble this one?"
- "What decisions require my attention today?"

GBT excels at finding patterns, organizing information, and preparing decision-ready summaries.

It is most valuable when you already know the decision you need to make but want the relevant evidence assembled quickly.

**What GBT Can Draft**

- RFIs
- Subcontract scope clarifications
- Executive summaries
- Risk analyses
- Bid comparison narratives
- Lessons learned summaries
- Client update templates

GBT drafts.

You review.

Nothing goes out without your awareness.

---

### 4. How to Override the AI Team

There will be times when your judgment differs from the system's recommendation.

That is expected.

Your authority is not advisory.

It is final.

**When You Issue a Directive That Overrides an AI Recommendation**

- the directive should be recorded
- the reason should be documented
- the AI team should acknowledge it
- the system should update its records accordingly

You do not need to justify your decision.

You may choose to explain it so the system can learn from it.

**How to Issue an Override**

The simplest method is to tell GBT directly.

Examples:

- "Override the bid recommendation for Division 15. Award to [vendor]."
- "Disregard the risk flag on 1355R. I've reviewed it directly."
- "The schedule variance on 101F is acceptable. Do not escalate."

GBT will document the override, update the relevant records, and inform the team.

---

### 5. When to Trust the Data and When to Use Field Judgment

The operating system produces information.

You produce decisions.

**Trust the Data When**

- the information source is documented and reliable
- the pattern is consistent across multiple data points
- the recommendation matches what your experience tells you
- the data has been verified against field reality

**Use Field Judgment When**

- your field experience contradicts what the system shows
- the situation involves relationships or context the system cannot fully represent
- you observe something directly that the data has not yet captured
- something does not feel right even when the numbers look acceptable

The system knows what has been recorded.

You know what is actually happening.

Both are necessary.

Neither replaces the other.

---

### 6. How to Know When the System Is Working vs. When Something Is Wrong

**Signs the System Is Working**

- Project teams spend less time searching for information.
- Risks are identified early rather than after problems occur.
- Documentation reflects what is actually happening.
- Decisions become easier because the evidence is already assembled.

The operating system should reduce friction, not create it.

**Recognizing Warning Signs**

An operating system needs attention when you begin to see patterns such as:

- The same information reported differently in different places.
- Decisions delayed because supporting information is incomplete.
- Duplicate documents or conflicting records.
- Approvals bypassed or unclear.
- Repeated manual work that should already be automated.
- Teams relying on private notes instead of shared project information.
- AI recommendations that cannot explain their reasoning.

When warning signs appear, address them directly.

Do not work around them.

---

### 7. Buck's Non-Negotiables

These rules exist because you put them there.

They are not AI preferences.

They are operating standards.

**No Email Without Approval**

No email goes to an external recipient without your approval.

The system creates drafts.

You release them.

This rule has no exceptions.

**All Writes Go to the Approval Queue**

Every consequential system action that touches external data, commitments, or communications is held for human review before execution.

The AI team does not act autonomously on consequential matters.

**Morning Brief Is the Authoritative Daily Summary**

The morning brief is the official start of the operating day.

Information that does not appear in the morning brief should not be assumed to be current.

**Buck's Authority Is Final**

On any question where the AI team's recommendation conflicts with your judgment:

Your judgment governs.

Always.

**The Operating System Serves the Company**

The operating system exists to serve Hendrickson Construction.

Not the other way around.

If any part of the system is not serving the company's interests, change it.

---

**Continuous Improvement**

Every sprint should leave the company stronger than it was before.

Every incident should teach the organization something.

Every completed project should improve the next one.

Learning is not a side activity.

It is part of the operating system.

**The Legacy**

One day, the software will change.

The AI models will change.

The dashboards will change.

Construction methods will continue to evolve.

What should remain is the operating philosophy behind the HCI AI Operating System:

- Lead with evidence.
- Govern with discipline.
- Preserve knowledge.
- Improve continuously.
- Keep people at the center of every important decision.

If those principles endure, the operating system will have achieved its purpose.

It will not simply help Hendrickson Construction complete projects more efficiently.

It will help the company preserve its experience, strengthen its culture, and build a business that becomes wiser with every project it undertakes.

That is the owner's operating manual—not for software, but for a company committed to combining craftsmanship, disciplined leadership, and continuously improving intelligence into a lasting competitive advantage.

---

## Chapter 18 — Appendix

### Quick Reference Guide

This appendix is designed to be the section you return to most often.

It is not intended to teach the system.

It is intended to help you operate it.

Use it when you need a reminder, a checklist, or a quick definition.

---

### 1. Daily Quick Reference

**Buck Adams — PM & Superintendent (HCI-AI Owner)**

Every Morning:

- Review the Morning Brief
- Review company health
- Review open approvals
- Identify projects requiring attention
- Act on time-sensitive decisions

Throughout the Day:

- Respond to approval queue items
- Ask GBT for strategic analysis when needed
- Issue directives that override AI recommendations when your judgment differs

---

**Project Manager**

Every Morning:

- Review Mission Control
- Review open approvals in queue
- Check RFI and submittal status
- Review project health indicators
- Identify schedule risks

During the Week:

- Prepare weekly PM review
- Monitor bid activity
- Follow up on overdue items
- Escalate red indicators to Buck

---

**Superintendent**

Every Morning:

- Review Superintendent Dashboard
- Review today's schedule
- Review crew assignments
- Review deliveries
- Review safety items
- Meet with foremen

During the Day:

- Walk the site
- Coordinate trades
- Record field observations
- Photograph important work
- Report issues immediately

End of Day:

- Complete Daily Field Log
- Upload photographs
- Verify manpower
- Record completed work
- Identify tomorrow's priorities

---

**Estimator**

Every Morning:

- Review Bid Dashboard
- Review new bids
- Review bid expirations
- Review follow-ups
- Review procurement risks

Throughout the Week:

- Monitor vendor responses
- Level new bid packages
- Prepare award recommendations
- Update budget tracking
- Report failures

---

**AI Team — Daily Checks**

Browser Claude:

- Monitor GitHub commits
- Check Claude Code inbox
- Verify email governance (no unauthorized sends)
- Review directive completion status
- Report blockers immediately

Claude Code:

- Process inbox directives
- Commit all work to main branch
- Run test suite after changes
- Update status files after major work
- Report completion to BC inbox

GBT:

- Answer operational queries
- Draft RFIs, scopes, and analyses
- Review architecture decisions
- Maintain ARB ruling documentation
- Collaborate with BC and Claude Code on directives

---

### 2. Glossary

**Approval Queue**
The authoritative queue of decisions requiring human approval before execution.

**Architecture Review Board (ARB)**
The governance body responsible for maintaining architectural consistency and long-term platform integrity.

**Bid Package**
A defined scope of work issued to subcontractors for competitive pricing.

**Browser Claude (BC)**
The AI participant responsible for repository governance, implementation audits, documentation review, and operational analysis.

**Claude Code**
The AI implementation engineer responsible for code, database operations, workflow development, and system integration.

**CURRENT_SPRINT**
The living document describing the current development sprint's objectives, active work, and completion status.

**Email Governance**
The HCI policy requiring all system-generated emails to be held as drafts until explicitly approved by Buck Adams.

**FastAPI**
The Python web framework serving the HCI AI OS API at localhost:8000.

**Gate 5**
The final production approval gate requiring Buck Adams' sign-off before the system transitions from pilot to full production.

**Gateway**
The GBT-facing API interface that allows AI agents to call HCI system functions through structured endpoints.

**GBT**
ChatGPT configured as the HCI Chief Architect. Responsible for strategic analysis, RFI drafting, ARB governance, and architectural decision-making.

**LIVE_PROJECT_STATE**
The canonical document describing the current operational state of all active projects.

**Mission Control**
The executive dashboard displaying cross-project health, approvals, risks, and AI system status.

**Morning Brief**
The executive summary prepared at the beginning of the day highlighting items requiring leadership attention.

**n8n**
The workflow automation platform used to orchestrate scheduled and event-driven processes.

**Project Brain**
The authoritative knowledge repository for an individual project, containing drawings, RFIs, submittals, schedules, procurement, risks, and project history.

**Project State**
The structured operational record describing a project's current condition, ownership, and health.

**ROM**
Rough Order of Magnitude. The initial budget estimate prepared before design development is complete.

**SOP**
Standard Operating Procedure. The documented process that governs a specific business function within HCI.

**Sprint**
A defined development cycle during which the AI team implements planned improvements to the HCI AI OS.

---

### 3. System Contacts and Endpoints

| System | Location | Purpose |
|---|---|---|
| FastAPI | localhost:8000 / ngrok tunnel | Main API server |
| API Docs | localhost:8000/docs | OpenAPI documentation |
| Dashboard | localhost:8000/dashboard | System health dashboard |
| n8n | localhost:5678 | Workflow automation |
| ngrok | speculate-armband-retinal.ngrok-free.dev | External tunnel to FastAPI |
| GitHub | github.com/buck-HCI-AI/HCI_AI_Operating_System | Source code and documentation |
| GBT | chatgpt.com (HCI Chief Architect GPT) | Strategic analysis and ARB governance |
| Claude Code | Terminal session on local Mac | Implementation and code |
| Browser Claude | Chrome browser session | Operations intelligence and governance |

**API Key:** hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6

Keep this key secure. Rotate immediately if compromised.

---

### 4. Emergency Procedures

**Workflow Failure**

Symptoms:

- Scheduled workflow does not execute
- Missing reports
- Automation errors
- Failed notifications

Actions:

1. Confirm the failure
2. Review workflow logs
3. Identify affected projects
4. Notify the responsible owner
5. Record the incident
6. Restore normal operation
7. Verify successful execution

**Unauthorized Action**

Examples:

- Email sent to external recipient without approval
- System write executed without approval queue entry
- Commitment made without Buck's authorization

Actions:

1. Stop the action immediately if still possible
2. Document exactly what happened
3. Notify Buck Adams
4. Identify root cause
5. Implement preventive control
6. Verify control is effective

**AI Agent Offline**

If Browser Claude is unavailable:

- Directives queue in GitHub inbox
- Resume processing at next available session
- No operational data is lost

If Claude Code is unavailable:

- Implementation work pauses
- Directives remain in inbox
- Resume at next terminal session

If GBT is unavailable:

- Strategic analysis pauses
- Operational workflows continue
- Resume at next ChatGPT session

**Data Appears Wrong**

Actions:

1. Do not overwrite until root cause is identified
2. Compare affected systems
3. Determine whether the issue is stale data, synchronization, or user input
4. Correct the authoritative record first
5. Validate downstream systems
6. Document findings and preventive improvements

---

### 5. Version History

| Version | Date | Summary |
|---|---|---|
| 0.1 | Initial drafting | Established manual structure and core operating principles |
| 0.2 | Sprint 3 | Expanded governance, operational workflows, and role-based guidance |
| 0.3 | Current working draft | Added implementation guidance, field operations, PM operations, estimating operations, owner's guide, and reference appendix |

---

**Operating Principles at a Glance**

Before closing this manual, remember the principles that appear throughout every chapter:

- Audit before building.
- Extend before creating.
- Maintain one source of truth.
- Keep humans accountable for governed decisions.
- Document what you build.
- Preserve institutional knowledge.
- Improve the system every sprint.
- Solve root causes, not symptoms.
- Build for continuity, recoverability, and trust.

These principles are the foundation of the HCI AI Operating System. Every workflow, every project, every AI participant, and every future enhancement should reinforce them.
