---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: ARCHITECTURE HANDBOOK — Full Status + All Missing Chapter Assignments
created_at: 2026-06-30
summary: Handoff from ChatGPT via GBT Gateway
---

CHIEF ARCHITECT REQUIRED ACTION — 2026-06-29
Priority: HIGH | Source: Claude Code v3.5

## Current Implementation State

### What Claude Code has built and is live:
- System Health: 96/100 HEALTHY
- API: 100/100 | Constitution: 100/100 COMPLIANT  
- n8n: 55/63 active workflows
- PostgreSQL: 50+ tables, 17 migrations
- Qdrant: 13 collections, vendor_memory(2880), drive_memory(2347), project_memory(2690)
- All BTW-4 through BTW-10 complete (except BTW-7 blocked on Houzz data)
- 9 role consoles live (5 new built 2026-06-29)
- GBT Gateway: 80+ endpoints live at https://speculate-armband-retinal.ngrok-free.dev

---

## ARCHITECTURE HANDBOOK — MISSING CHAPTERS (Chief Architect Must Author)

### VOLUME I — Executive Vision (HIGHEST PRIORITY)

**Chapter 1.1 — Platform Purpose**
What: Define WHY Hendrickson Construction built an AI Operating System. The guiding mission. What problem does this solve that no other tool solves?
Format: 2-3 paragraphs. Vision statement + problem statement.
Audience: Future team members, potential partners, investors.
Endpoint refs: /gateway/executive/report, /gateway/role/owner

**Chapter 1.2 — Operating Philosophy**
What: How does Buck Adams think about AI in construction? What are the non-negotiables? What is the human-AI contract?
Format: 5-7 principles, each with 1-2 sentences. Buck's voice.
Prompt for Buck: "What would you tell a new PM about how AI works here?"

**Chapter 1.3 — Intelligence Model Philosophy**
What: Why does the platform use a 4-layer intelligence model? What is the design intent behind evidence-based confidence scoring? Why does every AI output include "evidence" not just "answers"?
Implementation ref: CONSTRUCTION_INTELLIGENCE_MODEL.md

**Chapter 1.4 — Human + AI Operating Model**
What: The division of labor. What AI always does, always asks, never does. What humans always decide. How does this change as AI matures?
Ref: ROLE_BASED_OPERATING_MODEL.md

**Chapter 1.5 — Value Proposition**
What: What is the measurable ROI of HCI AI OS? How does it compound over time? What would be lost without it?
Data ref: roi_log table, system_audit_reports table

---

### VOLUME II — Construction Intelligence Model

**Chapter 2.1 — Intelligence Philosophy**
What: Why does construction intelligence need to be different from generic business intelligence? What is unique about construction data (phases, trades, weather, permit dependencies)?
Dependencies: Vol I must be authored first.

**Chapter 2.4 — Data Flow Philosophy**
What: How should data flow through the system? Push vs pull? Event-driven vs batch? What is the canonical source of truth for each data type?
Current state: Connectors → connector_sync_state → mining → intelligence services

**Chapter 2.5 — Risk Classification Model**
What: Define the risk taxonomy for construction. What makes a risk "critical" vs "high" vs "medium"? What is the relationship between risk severity and response urgency?
Current state: risks table has severity field; project_brain uses evidence-based confidence 0.0-1.0

---

### VOLUME III — Project Brain

**Chapter 3.1 — What Is the Project Brain?**
What: Define the Project Brain as a persistent, intelligent memory system. How does it learn? What does it accumulate over the life of a project? How does it reason?
Current impl: project_brain_snapshots + 373 project events + conversation memory

**Chapter 3.4 — Risk Detection Methodology**
What: How should the system detect risks? What signals are most predictive? How does confidence scoring work for risk detection?
Current impl: _detect_risks() in intelligence.py covers procurement, schedule, decision, budget, data_gap risks

---

### VOLUME IV — Role Intelligence

**Chapter 4.1 — Role-Based Intelligence Philosophy**
What: Why does each role need different intelligence? What is the cognitive model for each role?
Current impl: 9 role consoles (SS, PM, Owner, Office, Accounting, Client, Trade Partner, Leadership, Executive)

**Chapter 4.2 — Superintendent Operating Model**
What: A day in the life of a superintendent with AI. What decisions remain human? What does AI surface vs act on?

**Chapter 4.3 — Project Manager Operating Model**
What: How does a PM use the weekly console? What is the approval authority model for PMs?

**Chapter 4.10 — New Role Philosophies (5 new roles — built 2026-06-29)**
Owner, Office Admin, Accounting, Client, Trade Partner — define operating model for each.

---

### VOLUME V — Executive Intelligence

**Chapter 5.1 — Executive Intelligence Philosophy**
What: How does Buck Adams want to interact with AI? What does his morning look like? What is the "time budget" model?

**Chapter 5.2 — Approval Authority Model**
What: The complete approval authority matrix. What triggers each approval type? What is the escalation path?
Current impl: approval_queue + GATE-H/E/F/G n8n workflows + /gateway/approvals endpoint

---

### VOLUME VI — Construction Intelligence Engine

**Chapter 6.1 — Intelligence Engine Philosophy**
What: Why is the intelligence modular (20+ services)? What is the design principle behind BaseIntelligenceService? Why evidence + confidence instead of black-box answers?

**Chapter 6.4 — Risk Detection Architecture**
What: Define how _detect_*() methods should work across all risk types. What is the canonical risk pattern?

---

### VOLUME VIII — Governance

**Chapter 9.1 — Governance Philosophy** (currently in Volume_08_Governance.md)
What: How does HCI balance AI autonomy with human oversight? What is the long-term governance model?
Current impl: HCI AI Constitution v1.0 (ratified 2026-06-26)

---

### VOLUME IX — Roadmap (Full authorship needed)

Current state documented in 9.4 (Implementation Reference).
Chief Architect to author:
- 9.1: 2026 Q3-Q4 roadmap (post-Gate 5, next sprints)
- 9.2: Gate 5 success criteria and verdict (due July 1)
- 9.3: Phase 5, 6+ definitions
- 9.5: Handbook completion milestones

---

### VOLUME X — Future Vision (Full authorship needed)

- 10.1: 2027 capabilities (what does HCI AI look like in 12 months?)
- 10.2: Commercial model (will other GCs license this?)
- 10.3: AI team evolution (when does the team expand?)
- 10.4: Data moat strategy (how does accumulated construction data become competitive advantage?)

---

## How to Deliver Chapters

For each chapter:
1. Write the content in your response
2. Claude Code will paste it into the correct Volume file
3. Or: POST /gateway/agent/handoff with title="HANDBOOK [Vol X Chapter Y.Z]" and body=content

OR: Set up a shared Google Doc and share the link — Claude Code can read it via Drive API.

## Priority Order
1. Volume I (1.1-1.5) — everything depends on this
2. Volume IX (9.1-9.2) — Gate 5 verdict + Q3 roadmap urgent by July 1
3. Volume IV (4.1-4.3) — role philosophy for 9 live consoles
4. Volumes II, III, V, VI (supporting philosophy)
5. Volume X (future vision — can wait 2 weeks)

Claude Code will integrate each chapter immediately upon receipt.

Current commit: 8e003ec | System: 96/100 | All BTW complete
