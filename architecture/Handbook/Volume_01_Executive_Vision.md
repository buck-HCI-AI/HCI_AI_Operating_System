# Volume I — Executive Vision
*HCI AI Construction Operating System Architecture Handbook*
**Status: PARTIALLY AUTHORED — Sections 1.A–1.D published by Buck Adams 2026-06-27**

---

## 1.A HCI AI Organization
*Authored by: Buck Adams (HCI Chief Designer / Platform Owner) — 2026-06-27*

```
Chris Hendrickson
Owner — Hendrickson Construction, Inc.
Final Authority on all construction contracts and business decisions
        |
        ▼
Buck Adams
PM / Senior Superintendent / Owner — HCI AI Operating System
HCI AI System Owner / Final Authority on AI operations and platform decisions
        │
        ▼
Chief Architect
(ChatGPT)
Responsible for:
  • Architecture
  • Operating Model
  • AI Intelligence Design
  • Long-Term Vision
        │
        ▼
Lead Implementation Engineer
(Claude Code)
Responsible for:
  • Implementation
  • Testing
  • Documentation
  • Synchronization
        │
        ▼
Discovery Engineer
(Browser Claude)
Responsible for:
  • External Systems
  • Reverse Engineering
  • Platform Intelligence
        │
        ▼
Automation Orchestrator
(n8n)
Responsible for:
  • Workflow
  • Scheduling
  • Notifications
        │
        ▼
Construction Intelligence Platform
  ├── Construction Intelligence Engine
  ├── Project Brain
  ├── Role Intelligence
  ├── Mission Control
  ├── Weekly Reporting
  └── Predictive Engine
```

**Authority model:**
Buck Adams holds final authority on all decisions. No AI agent, workflow, or automation issues external commitments, approves contracts, or makes financial decisions without Buck's explicit approval.

---

## 1.B Design Principles
*Authored by: Buck Adams (Chief Architect) — 2026-06-27*

These principles are the filter for every future feature decision.

> **"Does this help someone build a better project?"**
> If yes — it belongs. If the answer is "it's technically impressive" — it probably waits.

**1. One source of truth.**
Data lives in one place. The platform reads from that source — it does not copy, duplicate, or maintain parallel records.

**2. AI summarizes instead of duplicating.**
When information exists in Houzz, HubSpot, or Drive, the platform reads and summarizes it. It does not recreate or replace those systems.

**3. Enter information once.**
A Superintendent enters a daily log once. A PM enters a bid once. The platform distributes that information to every role that needs it automatically.

**4. Mobile first.**
The Superintendent is in the field. Every feature must work on a phone or tablet before it works on a desktop.

**5. Superintendent first. PM second. Leadership third.**
Field impact drives feature priority. If a feature doesn't help the person building the project, it doesn't ship before one that does.

**6. Every release must reduce work.**
A new capability that adds steps, clicks, or cognitive load is not a release — it's technical debt. Every deployment must make someone's day easier.

**7. AI recommends. Humans commit.**
The AI surfaces options, risks, and recommendations. Buck Adams, the PM, and the Superintendent make the commitments. This is non-negotiable.

**8. Every decision is traceable.**
If the platform recommends something, the evidence behind that recommendation is visible. No black boxes.

**9. Every project becomes smarter than the last.**
Lessons, costs, vendor performance, and risk patterns from completed projects automatically inform estimates, bids, and decisions on the next project.

---

## 1.C HCI AI Maturity Model
*Authored by: Buck Adams (Chief Architect) — 2026-06-27*

Every feature maps against this model. Features should pull the company up the maturity ladder — not sideways.

| Level | Name | Description | HCI Status |
|-------|------|-------------|-----------|
| 1 | **Connected** | All systems linked; data flows in | ✅ Achieved |
| 2 | **Integrated** | Data is unified; single source of truth | 🟡 In progress — Houzz data pending |
| 3 | **Intelligent** | AI surfaces risks, insights, recommendations | ✅ Achieved — 95/100 health |
| 4 | **Predictive** | AI forecasts outcomes before they happen | 🟡 In progress — pending Houzz data |
| 5 | **Autonomous** | AI acts within defined authority; humans approve exceptions | 🔵 Designed — pending Pilot approval |

**Mapping rule:** Before building any new feature, identify which maturity level it supports. The Operational Readiness Review (ORR-001) gates the move to production.

---

## 1.D The North Star
*Authored by: Buck Adams — 2026-06-27*

> "When do we stop building this and it becomes a field tool?"

From this point forward, every new capability answers one question:

**"Does this help someone build a better project?"**

This is the philosophy that will keep the HCI AI Operating System focused on what matters most: making Hendrickson Construction more effective every single day.

---

## 1.1 Platform Purpose and Governance

*Authored by: GBT Chief Architect — 2026-07-02 (verified via getMissionControl)*

The HCI AI Operating System (HCI AI OS) is the governance and operational coordination platform supporting Hendrickson Construction Inc.'s preconstruction workflows. Its purpose is to provide a verified, auditable source of truth for project intelligence, architecture decisions, AI coordination, and executive reporting.

The system follows a **verify-before-claim** governance model (ADR-016). Any statement regarding project status, system capability, or completion must identify the evidence used for verification. If a claim cannot be confirmed against the live system, it must be marked **Unverified** rather than presented as fact.

The Chief Architect (ChatGPT) serves as the Architecture Review Board (ARB) lead, responsible for: maintaining architectural governance and documentation; reconciling Handbook content against the live implementation; identifying documentation drift; and reviewing cross-agent design decisions before they become canonical guidance.

Implementation responsibilities are delegated to **Claude Code**, which owns software development, testing, deployment, production stabilization, and implementation of approved architectural decisions. **Browser Claude** owns repository governance, documentation synchronization, and repository integrity. **n8n** is the automation platform; however, its operational status must always be verified against live telemetry before documentation states it is active.

Mission Control is the authoritative operational dashboard for executive status. Handbook text should describe the architecture and identify Mission Control as the source of operational truth rather than hard-coding transient metrics.

Because all current pilot projects remain in **preconstruction** until permits are issued, Handbook guidance must not infer active field construction, schedule progress, or daily site operations from historical test data. Any construction-state assertions require verification through the live system before publication.

---

## 1.2 Operating Philosophy (⚠️ Chief Architect — ChatGPT authorship pending)

*[Chief Architect: Expand on the Design Principles in 1.B — the philosophy behind how the platform operates.]*

---

## 1.3 Intelligence Model Philosophy (⚠️ Chief Architect — ChatGPT authorship pending)

*[Chief Architect: What does "intelligence" mean in a construction context?
How is construction intelligence different from generic business intelligence?]*

---

## 1.5 Value Proposition (⚠️ Chief Architect — ChatGPT authorship pending)

*[Chief Architect: What measurable value does the platform deliver to HCI?
Time saved? Risk reduced? Revenue protected? Quality improved?]*

---

## 1.6 Implementation Reference (Claude Code — DO NOT OVERWRITE)

**Current Platform Value (Gate 5 Pilot — 2026-06-25 → 2026-07-01):**
- 1,784 minutes (29.7 hours) saved in first 2 days
- 62 documents processed autonomously
- 31 risks detected and surfaced
- 3 active projects monitored continuously
- 95/100 system health

**Active intelligence layers:**
1. Project Brain — per-project health, risks, opportunities
2. Cross-Project — portfolio health matrix, company snapshot
3. Predictive Engine — 7 forward-looking risk categories
4. Executive Mission Control — 11-section leadership dashboard

**AI team operating model (current):**
- Claude Code: Lead Implementation Engineer + Handbook Maintainer
- ChatGPT: Chief Architect + Integration Director
- Browser Claude: Discovery Agent (Houzz/HubSpot data extraction)
- n8n: Automation Orchestrator (15 workflows, 7 active)
