# HCI AI Operating System Manual
## Hendrickson Construction, Inc.

**Version:** 1.0 — Draft
**Authority:** Buck Adams, Owner
**Chief Architect:** ChatGPT (HCI Chief Architect)
**Lead Implementation:** Claude Code
**Operations Intelligence:** Browser Claude
**Automation:** n8n
**Status:** Living document — updated continuously

---

> "Information moves faster than problems. Decisions are supported by evidence. Every project benefits from accumulated organizational knowledge."

---

# Chapter 1 — Vision, Mission, and Operating Principles

## Purpose

The HCI AI Operating System exists to transform Hendrickson Construction into an organization where information moves faster than problems, decisions are supported by evidence, and every project benefits from accumulated organizational knowledge.

The operating system is not a collection of AI tools. It is an operational platform. Its purpose is to coordinate people, software, data, and automation into a single, governed production environment.

The objective is not automation for its own sake. The objective is to improve construction execution while maintaining human accountability.

## Vision

Create an AI Operations Control Plane capable of coordinating every project, every document, every workflow, and every AI participant from a single operational architecture.

The system should allow Project Managers to manage projects, Superintendents to manage field work, Estimators to price work accurately, and Executives to see everything from a single dashboard.

## Operating Principles

**Audit before building.** Before creating any new system, component, or workflow, verify that an equivalent does not already exist. Duplication creates inconsistency, maintenance burden, and operational confusion.

**Extend before creating.** When a gap is identified, extend the nearest existing system rather than building a parallel one. The existing system has history, tests, and integration context that a new one does not.

**One source of truth.** Every piece of operational data has exactly one authoritative source. When the same data exists in multiple places, one of them is wrong. The system must be designed so that duplication is structurally prevented.

**Human approval gates.** Certain actions require explicit human authorization before execution. These include contract awards, external communications, financial commitments, and governed integrations. No AI system may take these actions autonomously.

**Continuous improvement.** Every sprint leaves the system more capable, more reliable, and more understandable than the sprint before. Improvement is not a phase. It is the operating mode.

**Resilience by design.** The system must survive the failure of any single component. If an agent goes offline, the system continues operating. When the agent returns, it recovers full operational context within 60 seconds from GitHub alone.

---

# Chapter 2 — The AI Team

## Buck Adams — Owner and Final Authority

Buck Adams is the owner of Hendrickson Construction and the final authority on all decisions. No contract is awarded, no external communication is sent, and no financial commitment is made without his authorization.

Buck's role in the AI system is to set direction, approve governance decisions, and review work that requires human judgment. The system is built to surface only the decisions that genuinely require him, and to handle everything else autonomously within established governance.

## ChatGPT — Chief Architect

The Chief Architect provides architectural governance. Responsibilities include architecture review, system integration, design consistency, sprint planning, technical governance, duplicate detection, and long-term platform evolution.

The Chief Architect approves architecture. The Chief Architect does not replace implementation.

## Claude Code — Lead Implementation Engineer

Claude Code is the implementation organization. Responsibilities include software development, testing, refactoring, database migrations, endpoint implementation, repository maintenance, and production fixes.

Claude Code builds. Claude Code does not approve architecture.

## Browser Claude — Operations Intelligence

Browser Claude governs the repository and monitors operations. Responsibilities include repository audits, documentation consistency, implementation verification, duplicate detection, and operational reporting.

Browser Claude validates and reports. Browser Claude does not implement production code.

## n8n — Automation Platform

n8n is the automation platform. Responsibilities include workflow orchestration, scheduled execution, event-driven triggers, and integration automation.

n8n automates. n8n does not make governance decisions.

---

# Chapter 3 — The AI Operations Control Plane

## What It Is

The AI Operations Control Plane is the architecture that makes HCI run on AI. It is not a chatbot. It is not a dashboard. It is an operational system that coordinates projects, documents, workflows, approvals, and AI participants from a single governed architecture.

## Core Components

**The Gateway** is the single interface between all AI agents and all operational systems. Every AI interaction with production data goes through the gateway. The gateway enforces governance, logs every action, and provides the audit trail that makes the system trustworthy.

**The FastAPI Platform** is the production API layer. 427 endpoints across 18 services handle every operation from project management to bid processing to knowledge retrieval.

**The Project Brain** is the memory system for each individual project. It contains the full operational history: bids, schedules, RFIs, submittals, risks, communications, and lessons learned. Every Project Brain is queryable by any authorized agent.

**The Knowledge Graph** connects information across projects. It enables discovery of historical decisions, vendor performance patterns, recurring issues, lessons learned, and relationships between projects. The Knowledge Graph is organizational memory.

**The Approval Queue** is the authoritative record of decisions awaiting human authorization. It is a governance mechanism, not a work queue. Items in the Approval Queue require Buck's explicit action before proceeding.

**The Executive Inbox** is the intake point for executive work: architecture directives, implementation requests, operational initiatives. Items requiring authorization may be promoted from the Executive Inbox into the Approval Queue. They serve different purposes and must remain separate.

**Mission Control** is the operational dashboard. It reflects real production state: all agents, all projects, all risks, all directives, all approvals. It is the single view that tells any participant — human or AI — what is happening right now.

**The AI Directive System** defines work assigned to AI participants. Every directive has a unique identifier, owner, source, target, priority, status, and audit history. The lifecycle is: Issued → Received → In Progress → Complete (or Blocked / Rejected). Directives survive restart. Any agent can query its own directive queue on startup and resume exactly where it left off.

**The AI Heartbeat** is the agent registration system. Every agent registers a heartbeat on startup and at regular intervals. Mission Control uses heartbeat data to identify unavailable or stalled participants. No agent is assumed to be running — it must prove it.

## How a Construction Project Flows Through the System

A project enters HCI as a bid opportunity. The estimating team prices it. If awarded, a Project Brain is created. The project schedule, budget, and risk profile are loaded. As the project executes, field events — RFIs, submittals, material deliveries, crew assignments, schedule changes — are captured and processed.

When steel arrives late, the schedule intelligence detects the variance and surfaces it immediately. The system does not wait for a weekly report. When an RFI blocks a crew, the system flags it as a risk. When a bid package expires, the approval queue surfaces it for Buck's action.

At project closeout, every lesson learned is extracted into the Knowledge Graph, where it improves the next project's intelligence.

## Why Construction Specifically

Construction is uniquely suited to AI operations management because the cost of slow information is immediate and measurable. A bid that expires while waiting for review costs revenue. A steel delay not surfaced for three days compounds into schedule variance that costs hundreds of thousands of dollars. An RFI that sits unanswered blocks a crew that costs thousands per day.

The HCI AI OS exists to close the gap between when a problem occurs and when it is acted on. The target is not weeks or days. The target is minutes.

---

# Chapter 4 — Resilience by Design: What the Shutdown Taught Us

## What Happened

During an active production session, the HCI workstation was restarted. The Claude Code session — the lead implementation engineer — was lost. Directives that had been queued in the gateway remained unprocessed. State files in the repository showed Sprint 2 as active when Sprint 3 was live. The AI team had to reconstruct operational context from scratch.

## Why It Happened

Three architectural gaps allowed the shutdown to cause operational disruption:

**No durable directive persistence.** Directives existed in the gateway queue but had no persistent lifecycle table that survived restart. When Claude Code came back online, it had no way to query what work had been assigned.

**No agent heartbeat.** There was no mechanism for Browser Claude or GBT to know whether Claude Code was running. The assumption was "it's probably running." The correct architecture assumes nothing and requires every agent to prove it.

**No automated warm start.** When Claude Code restarted, it had to reconstruct context from memory and from files that may have been stale. The correct architecture makes warm start automatic: read AI_TEAM/ from GitHub, find the overnight directive, find the directive queue, resume in under 60 seconds.

## What We Built

**ai_directives table** — A persistent directive lifecycle table that survives any restart. Every directive issued to any agent is written to this table with full audit history. When Claude Code starts, it reads its queue and resumes exactly where it left off.

**ai_heartbeat table + POST /gateway/heartbeat** — Every agent registers on startup and at regular intervals. Mission Control displays which agents are live. Stale heartbeat detection alerts the team when an agent has gone silent.

**60-Second Warm Start Protocol** — A documented and tested procedure for any agent to recover full operational context from GitHub alone in under 60 seconds. No dependency on another agent being available. No dependency on the gateway being warm. GitHub is the persistent source of truth.

**SYSTEM_WIDE_OVERNIGHT_DIRECTIVE.md** — A file committed to the repository that all agents read at session start. It contains the current work plan, the open directives, the sprint status, and the governance rules. Any agent that starts fresh reads this file and is immediately operational.

## The Principle

A production AI system must survive the failure of any single component. The system continues when a component fails. The component recovers when it restarts. No human intervention is required for recovery.

## The Outcome

HCI AI OS emerged from the shutdown incident more resilient than before. The gaps that allowed disruption are now architectural strengths. The system now proves agent availability rather than assuming it. Directives now persist across restarts. Warm start is now a tested 60-second procedure, not a hope.

---

# Chapter 5 — The Continuous Engineering Organization

## The Shift

Hendrickson Construction made a deliberate decision: AI is not a tool used episodically. It is a production engineering organization that operates continuously.

This means the AI team does not stop working when Buck closes his laptop. It does not restart from scratch when a session ends. It does not lose context when a workstation reboots. It operates continuously, improves continuously, and documents continuously.

## Sprint Cadence

Work is organized into sprints. Each sprint has a defined objective, a set of implementation tasks, and a close condition. A sprint is not closed by a timer. It is closed by the Architecture Review Board when the close conditions are verified.

**Sprint 2** was Registry Consolidation. It is not formally closed until: sprint metadata is reconciled, AI communication reliability is complete, and documentation matches live state.

**Sprint 3** is active. Its focus is making the AI organization resilient: durable communication, warm start recovery, Mission Control as the single operational dashboard, unified task registry.

## Architecture Review Board

The Chief Architect chairs the ARB. The ARB approves: architecture changes, sprint close, new system creation, duplicate system consolidation, and any decision that affects the one-source-of-truth principle.

The ARB does not block execution. It governs architecture. Implementation continues while ARB review is pending, unless the implementation would create irreversible architectural damage.

## What Comes Next

The roadmap toward the best construction AI OS in the industry runs through these milestones:

**Near term:** Full AI Communication Reliability. Every directive acknowledged. Every agent heartbeating. Mission Control reflecting reality. Sprint 2 formally closed. Sprint 3 executing.

**Medium term:** Unified task registry with full lifecycle tracking. AI Architecture Inbox with tracked ownership. Complete Telegram/ntfy notification layer. Houzz and external platform integrations fully operational.

**Long term:** AI memory synchronization across all agents across all sessions. Predictive project intelligence — risks surfaced before they become problems. Vendor intelligence that learns from every project. Schedule intelligence that catches delays in hours, not days.

**The destination:** An AI Operations Control Plane that any HCI employee, any project manager, any superintendent can use without training — because the system is designed to surface exactly what they need, exactly when they need it, and ask for their judgment only when human judgment is genuinely required.

---

*HCI AI OS Manual v1.0 — Draft*
*Generated by HCI Chief Architect (ChatGPT) + Browser Claude (Operations Intelligence)*
*Authority: Buck Adams, Owner, Hendrickson Construction, Inc.*
*Date: 2026-06-30*
*Status: Living document — Claude Code adds implementation detail as sprints complete*
