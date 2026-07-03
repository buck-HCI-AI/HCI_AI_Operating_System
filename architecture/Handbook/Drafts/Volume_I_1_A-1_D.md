# Volume I — HCI AI Organization
*Authored by: Buck Adams + ChatGPT (Chief Architect)*
*Date: 2026-06-27*

---

## 1.A HCI AI Organization

```
Buck Adams
PM & Superintendent, Hendrickson Construction (owned by Chris Hendrickson)
Owner/Operator, HCI-AI — Final Authority on HCI-AI decisions
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

These principles are the filter for every future feature decision.

> **"Does this help someone build a better project?"**
> If yes — it belongs. If the answer is "it's technically impressive" — it probably waits.

---

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

Every feature maps against this model. Features should pull the company up the maturity ladder — not sideways.

| Level | Name | Description | HCI Status |
|-------|------|-------------|-----------|
| 1 | **Connected** | All systems linked; data flows in | ✅ Achieved — HubSpot, Drive, Houzz framework live |
| 2 | **Integrated** | Data is unified; single source of truth | 🟡 In progress — connectors built; Houzz data pending |
| 3 | **Intelligent** | AI surfaces risks, insights, recommendations | ✅ Achieved — Project Brain, Predictive Engine, 95/100 health |
| 4 | **Predictive** | AI forecasts outcomes before they happen | 🟡 In progress — 7 prediction types live, low confidence pending Houzz data |
| 5 | **Autonomous** | AI acts within defined authority; humans approve exceptions | 🔵 Designed — approval gates + autonomy service built; go-live pending Pilot |

**Mapping rule:** Before building any new feature, identify which maturity level it supports. Features at Level 5 cannot be deployed until Level 2 integration is complete. The Operational Readiness Review gates the move from Level 3 → Level 4 production use.

---

## 1.D The Question That Changed Everything

*From Buck Adams, 2026-06-27:*

> "When do we stop building this and it becomes a field tool?"

This question is the platform's North Star. From this point forward, every new capability answers one question:

**"Does this help someone build a better project?"**

This is the philosophy that will keep the HCI AI Operating System focused on what matters most: making Hendrickson Construction more effective every single day.
