# UNIFIED_STATE_MODEL_SPEC.md
## HCI AI OS — Unified Operational State Model

**GBT Designation:** #1 Architectural Priority for Sprint 3
**Authored by:** Browser Claude (from GBT Cycle 5 design)
**Date:** 2026-07-01
**Status:** Implementation-ready — pending Claude Code

---

## Problem Statement

Every AI agent session starts cold. Browser Claude opens a new conversation with no knowledge of what was accomplished in the previous session. GBT starts without knowing what directives are queued. Claude Code restarts without knowing which tasks were in progress.

This cold-start problem means that every session begins with context reconstruction: reading commit history, parsing status documents, identifying what was last done, and determining what comes next. This process takes time and is error-prone.

A Unified Operational State Model eliminates the cold-start problem. It is a structured, always-current document in the repository that any agent can read to immediately understand the full operational state of HCI AI OS.

---

## Solution: The Operational State Document

A single JSON file — `AI_TEAM/OPERATIONAL_STATE.json` — maintained at all times as the authoritative operational state of the system.

**File path:** `AI_TEAM/OPERATIONAL_STATE.json`
**Format:** JSON (structured, machine-parseable)
**Updated by:** Any agent after completing work. Updated by WF-AI-001 on heartbeat cycle.
**Read by:** Any agent at session start (first action before any other work)

---

## State Document Schema

```json
{
  "schema_version": "1.0",
  "last_updated": "2026-07-01T14:32:00Z",
  "updated_by": "browser_claude",

  "sprint": {
    "id": "sprint_3",
    "name": "Production Hardening + Communications Layer",
    "status": "ACTIVE",
    "opened": "2026-07-01",
    "close_conditions": [
      "Email governance gate verified in code",
      "Telegram bot deployed and tested",
      "WF-AI-001 auto-restart deployed",
      "Unified State Model deployed",
      "Claude Code back online with Sprint 3 context"
    ],
    "close_conditions_met": []
  },

  "directives": {
    "active": [
      {
        "id": "DIR-2026-0001",
        "title": "Expand manual chapters 6-12 to publish quality",
        "state": "COMPLETED",
        "assigned_to": "browser_claude",
        "completed_at": "2026-07-01T15:00:00Z",
        "commits": ["affba36", "84eab40", "4e5524f"]
      },
      {
        "id": "DIR-2026-0002",
        "title": "Build TELEGRAM_AUTH_SPEC",
        "state": "COMPLETED",
        "assigned_to": "browser_claude",
        "completed_at": "2026-07-01T15:30:00Z",
        "commits": ["7ae48e0"]
      },
      {
        "id": "DIR-2026-0003",
        "title": "Implement email governance gate in FastAPI + n8n",
        "state": "QUEUED",
        "assigned_to": "claude_code",
        "blocked_by": "Claude Code offline",
        "dependencies": ["N8N_EMAIL_AUDIT_CHECKLIST.md", "EMAIL_ARCHITECTURE_REVIEW_2026-07-01.md"]
      },
      {
        "id": "DIR-2026-0004",
        "title": "Deploy Telegram bot and WF-TELE-001",
        "state": "QUEUED",
        "assigned_to": "claude_code",
        "blocked_by": "Claude Code offline + Telegram Bot Token needed from Buck",
        "dependencies": ["TELEGRAM_AUTH_SPEC.md", "TELEGRAM_ARCHITECTURE_SPEC.md"]
      },
      {
        "id": "DIR-2026-0005",
        "title": "Deploy WF-AI-001 auto-restart workflow",
        "state": "QUEUED",
        "assigned_to": "claude_code",
        "blocked_by": "Claude Code offline",
        "dependencies": ["AI_DIRECTIVE_LIFECYCLE_SPEC.md", "IDLE_MONITOR_SPEC.md"]
      }
    ]
  },

  "projects": {
    "active": [
      {
        "id": "101F",
        "name": "Project 101F",
        "health": "AT_RISK",
        "schedule_variance_days": -5,
        "data_issue": "1355R data discrepancy",
        "pm": "TBD",
        "superintendent": "TBD"
      }
    ]
  },

  "agents": {
    "browser_claude": {
      "status": "ACTIVE",
      "last_heartbeat": "2026-07-01T15:30:00Z",
      "current_task": "Committing UNIFIED_STATE_MODEL_SPEC.md",
      "session_commits": ["affba36", "84eab40", "4e5524f", "f6b1125", "7ae48e0"]
    },
    "gbt": {
      "status": "IDLE",
      "last_response": "2026-07-01T12:00:00Z",
      "last_directive": "Cycle 5 Part 2 — Unified State Model, Perplexity, CPM"
    },
    "claude_code": {
      "status": "OFFLINE",
      "last_commit": "2026-06-30",
      "last_known_task": "Sprint 2 implementation tasks",
      "queued_directives": ["DIR-2026-0003", "DIR-2026-0004", "DIR-2026-0005"]
    },
    "n8n": {
      "status": "RUNNING",
      "gateway_url": "https://speculate-armband-retinal.ngrok-free.dev",
      "known_issue": "7 email paths unverified for approval gate"
    }
  },

  "governance": {
    "email_direct_send_authorized": false,
    "email_governance_note": "BC_EMAIL_CAPABILITY.md direct send revoked commit e59ba38. Draft only until Code confirms gate.",
    "pending_buck_decisions": [
      "Gate 5 explicit go/no-go (GATE5_SIGNOFF_PENDING.md)",
      "Telegram Bot Token + Telegram User ID for integration",
      "Review BC_EMAIL_CAPABILITY.md governance update"
    ]
  },

  "system_config": {
    "gateway_url": "https://speculate-armband-retinal.ngrok-free.dev",
    "gateway_api_key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6",
    "local_fastapi": "http://localhost:8000",
    "local_n8n": "http://localhost:5678",
    "repository": "buck-HCI-AI/HCI_AI_Operating_System",
    "main_branch": "main"
  },

  "last_session_summary": "Session 2026-07-01: Expanded manual chapters 7, 8, 9, 10, 11, 12 to publish quality. Committed RECOMMENDED_TOOLS_SPEC (18 tools), TELEGRAM_AUTH_SPEC. Manual now 169KB. All chapters 1-18 publish quality. Cycles 2-5 completed with GBT. Sprint 3 specs committed and ready for Code."
}
```

---

## State Document Lifecycle

### On Session Start (Any Agent)

Every agent session begins with a single mandatory action: read `AI_TEAM/OPERATIONAL_STATE.json`.

Reading the state document answers:
- What sprint are we in? What are the close conditions?
- What directives are ACTIVE? What is their status?
- Which agent owns which directive?
- What projects are active? What are their health statuses?
- What decisions are pending Buck approval?
- What is the gateway URL and API key?
- What was accomplished in the last session?

From this single read, any agent can immediately operate without re-reading commit history or asking "what happened last time?"

### On Session End (Any Agent)

At session end, the agent updates the state document:
- Updates its own heartbeat timestamp
- Updates directive states (COMPLETED, BLOCKED, etc.)
- Adds session commits to the commit list
- Updates last_session_summary
- Commits the updated OPERATIONAL_STATE.json to main

### On Auto-Restart (WF-AI-001)

When the auto-restart workflow detects a stale agent:
1. Read OPERATIONAL_STATE.json
2. Identify ACTIVE directives assigned to the stale agent
3. Move those directives to QUEUED_RESTART state
4. Update agent status to OFFLINE
5. Send Telegram alert to Buck with the current state
6. Commit updated state document

---

## Implementation Plan

### Phase 1: Create Initial OPERATIONAL_STATE.json
**Owner:** Browser Claude (immediate)
**Action:** Create AI_TEAM/OPERATIONAL_STATE.json with current state based on this spec.
**Acceptance:** File exists in repository, is valid JSON, reflects current system state.

### Phase 2: Agent Session Start Protocol
**Owner:** All agents (immediate)
**Action:** Every agent session begins by reading OPERATIONAL_STATE.json. Behavior: if file does not exist, read CURRENT_SPRINT.md and reconstruct state manually, then create the file.
**Acceptance:** Agent session start includes state document read as documented first action.

### Phase 3: Agent Session End Protocol
**Owner:** Claude Code (implements the update logic)
**Action:** Gateway endpoint POST /gateway/state/update that accepts a state patch and merges it into the current state document, then commits.
**Acceptance:** After each session, OPERATIONAL_STATE.json reflects the completed work.

### Phase 4: WF-AI-001 Integration
**Owner:** Claude Code
**Action:** WF-AI-001 reads OPERATIONAL_STATE.json to identify stale agents and ACTIVE directives. Updates state on restart detection.
**Acceptance:** WF-AI-001 automatically updates OPERATIONAL_STATE.json when a restart is triggered.

---

## Gateway Endpoints Required

```
GET /gateway/state/current
  Returns: Full OPERATIONAL_STATE.json content

POST /gateway/state/update
  Body: {agent, patch_data, session_commits}
  Action: Merge patch into current state, update heartbeat, commit to repo
  Returns: {success, new_state}

POST /gateway/state/directive_update
  Body: {directive_id, new_state, notes}
  Action: Update specific directive state in OPERATIONAL_STATE.json

POST /gateway/state/heartbeat
  Body: {agent, current_task}
  Action: Update agent heartbeat timestamp in state document
```

---

## Why This Is the #1 Architectural Priority

GBT designated the Unified State Model as the #1 architectural priority in Cycle 5 for these reasons:

1. **It eliminates cold-start degradation.** Every session currently loses time to context reconstruction. The State Model eliminates this cost entirely.

2. **It enables true multi-agent coordination.** Currently, agents coordinate through commit messages and status documents that require interpretation. The State Model provides machine-parseable coordination.

3. **It supports WF-AI-001 auto-restart.** The restart workflow needs to know what was active and what needs to be re-queued. Without a structured state document, this requires parsing git history and status documents — unreliable and slow.

4. **It makes the system self-aware.** An operating system that does not know its own state is not an operating system. The State Model gives HCI AI OS a continuously current self-model.

5. **It creates the foundation for the Idle Monitor.** AUTO-IDLE-001 needs to read agent heartbeats. The State Model provides this directly.

---

*Specification authored by Browser Claude | Architecture designed by GBT Cycle 5 | 2026-07-01*
