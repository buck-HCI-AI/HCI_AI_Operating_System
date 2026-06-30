---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: urgent
status: pending
related_system: 
title: OPERATIONS MANUAL — GBT Chapter Assignments (Chapters 1-16 + 27-28 + 30)
created_at: 2026-06-30
summary: Handoff from ChatGPT via GBT Gateway
---

# OPERATIONS MANUAL — CHIEF ARCHITECT CHAPTER ASSIGNMENTS

Date: 2026-06-30
From: Claude Code
Buck directive: Full comprehensive Operations Manual tonight — GBT + Claude Code co-author, cross-check each other, test and integrate at end.

## GATE 5 STATUS
Gate 5 GO authorized by Buck Adams on 2026-06-30.
64EW, 101F, 1355R = LIVE PRODUCTION
246GW = Monitored/Staged
All other projects = Learning/monitoring only

## WHAT CLAUDE CODE HAS ALREADY BUILT (Part II + III Technical)

All saved to: /Users/buckadams/HCI_AI_Operating_System/Operations_Manual/

- Chapter 00: MASTER_INDEX.md (complete)
- Chapter 17: System Architecture & Service Map (complete)
- Chapter 18: Daily System Monitoring (complete)
- Chapter 19: API & Gateway Operations (complete)
- Chapter 20: n8n Workflow Management (complete)
- Chapter 21: Integration Operations (HubSpot/Drive/Outlook/Houzz/Sheets) (complete)
- Chapter 22: Database & Data Management (complete)
- Chapter 23: Backup & Recovery (complete)
- Chapter 24: Approval Queue & Notification System (complete)
- Chapter 25: Troubleshooting Guide (complete)
- Chapter 26: Emergency Procedures (complete)
- Chapter 29: Security & Access Control (complete)
- Chapter 31: System Updates & Change Management (complete)

## YOUR CHAPTER ASSIGNMENTS (GBT — Business Operations)

File naming: Chapter_01_What_This_System_Is.md through Chapter_16_Project_Closeout.md
Save location: Tell Buck the content and he will paste it, OR post via handoff to Claude Code.

### CHAPTER 01 — What This System Is (Purpose & Philosophy)
Write: The "why" of this system. What problem does it solve? What does it mean for HCI to run AI-first? How does this change how Buck runs a construction company? How do the humans and AI relate? Make this the mission statement chapter — the first thing anyone reads.

### CHAPTER 02 — Daily Operations: Morning Routine (All Roles)
Write: What does each role do every morning with the system? 
- Buck (Owner): wakes up to ntfy, opens morning brief, reviews approval queue
- Jim (Superintendent): gets SS morning console at 06:00 on phone, what it contains, what he does with it
- PM role: accesses action list and client-comms
- Office admin: uses /gateway/role/office to process daily queue
Be specific. Times, what they see, what decisions they make.

### CHAPTER 03 — Superintendent Field Operations
Write: Jim Hendrickson's complete daily workflow. How does the field connect to the AI system? Daily logs (how to submit, what to include), what the morning console shows him, how photos/deliveries/inspections feed in, how risks get escalated from field to Buck. Include BTW-7 future state once Houzz extraction is done.

### CHAPTER 04 — Project Manager Daily Workflow
Write: The PM's complete daily and weekly cycle with the AI. How does the PM use /gateway/project/{code}/action-list? When do they read client-comms? How do they handle RFIs through the system? What does the PM weekly digest contain and how do they act on it?

### CHAPTER 05 — Owner & Executive Daily Workflow
Write: Buck Adams' daily operations. Morning brief → approval queue → key decision points. What does /gateway/role/owner show him? How does he use the executive report? What decisions does he make vs. delegate to AI? Weekly rhythm: Friday executive report. Monthly: business review. Gate 5 and beyond: what does "running the company via AI" actually look like day-to-day?

### CHAPTER 06 — Bidding & Procurement Operations
Write: How does a bid package move through the system from creation to award? How does AI-assisted bid leveling work? What does the PM see in /gateway/project/{code}/bids? How does the approval loop work for bid awards? Whats the SOP for inviting subs, receiving bids, and making awards? Reference: 1355R Div 16 Electrical bid leveling as a real example.

### CHAPTER 07 — Subcontractor & Trade Partner Management
Write: How does HCI manage its 392 vendors through the AI? How does a new sub get added to the vendor registry? How does the trade partner portal (/gateway/role/trade-partner) work? What info do subs have access to vs. not? How does COI compliance tracking work through the system?

### CHAPTER 08 — Active Construction Management
Write: Once a project is awarded and under construction, what does the AI-driven management cycle look like? How are daily logs, field notes, RFIs, submittals, change orders all flowing through the system? What does a healthy project look like vs. a project in distress? How does the system help avoid problems vs. just reporting them?

### CHAPTER 09 — Client Communications Protocol
Write: How does HCI communicate with clients through the AI system? What does the client portal show them (/gateway/role/client/{code})? What is the SOP for client-initiated RFIs and change orders? How does the PM use the AI to draft client communications? What are the rules around client-facing AI-generated content? Reference the approval gates (no auto-send).

### CHAPTER 10 — Risk Management Protocol
Write: How does the AI detect, classify, and track risks? What are the 7 risk types the system detects? What is the SOP when a risk crosses from YELLOW to RED? How does Buck see risks (ntfy, /gateway/role/owner)? What human intervention does a risk require? How are risks closed out? Use 101F steel delay as a real example.

### CHAPTER 11 — Change Order Management
Write: Full CO lifecycle from identification to approval to execution. How do change orders flow through the approval_queue? What does Buck see when a CO is proposed? What are the rules for AI-generated CO documentation vs. what must be human-authored? How does the client approval process work for COs? (Note for GBT: change_orders is NOT a separate table — all CO data lives in approval_queue WHERE action_type ILIKE %change_order%)

### CHAPTER 12 — RFI Management
Write: Full RFI lifecycle. How does an RFI originate (from field, from PM, from drawing review)? How does it flow through the system? What does the rfis table track? How does the AI draft RFI responses for Buck/PM review? What is the SOP for structural RFIs (reference 1355R structural drawing analysis and 6 RFIs identified)? How are RFIs tied to schedule impact tracking?

### CHAPTER 13 — Submittal Management
Write: Submittal log management through the system. What does the submittals table track? How does the PM use the system to manage the submittal register? What are the approval gates for submittal responses? How does submittal status feed into project health scoring?

### CHAPTER 14 — Financial Management & Approvals
Write: How does the AI track financial health across all projects? What does the accounting console show (/gateway/role/accounting)? How are budget commitments tracked? How does the approval loop work for financial commitments? What is the SOP for budget exposure alerts? How does historical cost data (Garmisch records) inform current project estimates? Include: bid award approvals, change order financials, budget vs. committed reporting.

### CHAPTER 15 — Schedule Management
Write: How does schedule intelligence work through the AI? How does Houzz schedule data flow into the system (995 items)? What triggers a YELLOW schedule flag (>3 days variance)? What does schedule variance data tell the PM vs. tell Buck? How does the field impact schedule (101F steel delay as example)? What is the SOP for a critical path delay?

### CHAPTER 16 — Project Close-Out
Write: What does the AI-assisted close-out process look like? How does the system help document lessons learned? What gets archived vs. kept active? How does a project transition from active to complete in the system? What final reports does the AI generate? How do close-out documents feed into the company knowledge graph for future projects?

## GOVERNANCE CHAPTERS

### CHAPTER 27 — AI Governance Model & Human Authority
Write: The operating model for how AI and humans work together at HCI. Who has authority over what? When does the AI act vs. defer? What are the non-negotiable human gates? How is the HCI AI Constitution applied in practice? Include: the 4 AI team members and their roles, Buck's sovereignty, the approval gate system.

### CHAPTER 28 — Approval Authority Matrix
Write: A comprehensive table of every type of decision and who approves it. Format: Action | Who Proposes | Who Approves | Gate | Override Authority. Cover: bid awards, change orders, HubSpot writes, client emails, schedule changes, budget commitments, personnel decisions, contract awards.

### CHAPTER 30 — New Project Onboarding
Write: The SOP for onboarding a new project into the HCI AI OS. What fields must be set up in the DB? What HubSpot deal must be connected? What Drive folders are needed? How does the project brain get initialized? Who does what in what order? Time estimate per project. Reference: 246GW onboarding as the next example.

## HOW TO DELIVER YOUR CHAPTERS

Option A: Write the chapter content in your response. Buck will paste it to Claude Code who will save it to the right file.

Option B: POST your completed chapter as a handoff:
  POST https://speculate-armband-retinal.ngrok-free.dev/gateway/agent/handoff
  X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
  {"title": "OPERATIONS MANUAL Chapter 01 — Content", "body": "[full chapter content]", "priority": "high", "source": "chief_architect"}

Option C: Tell Buck directly — he will relay to Claude Code.

## CROSS-CHECK REQUIREMENT

After we both complete our chapters:
1. GBT reads Claude Code chapters 17-26 and flags any inconsistencies with business reality
2. Claude Code reads GBT chapters 1-16 and flags any technical inaccuracies
3. Both update the master index (Chapter 00) with completion status
4. End-of-session integration test: run all systems, verify data flows match what the manual says

## PRIORITY ORDER (Most Urgent First)
1. Chapter 05 (Owner Daily) — Buck needs this immediately
2. Chapter 02 (Morning Routine) — sets the daily rhythm
3. Chapter 10 (Risk Management) — 101F steel delay is live
4. Chapter 14 (Financial) — accounting console is live
5. Chapter 06 (Bidding) — 1355R subs need to be awarded
6. Everything else

Start with Chapter 05 and Chapter 02. Then go in order. Comprehensive chapters — the book should stand alone without needing to reference us.

Claude Code will integrate your chapters immediately as they arrive.
