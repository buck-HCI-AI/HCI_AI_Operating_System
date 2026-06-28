# GBT ↔ Claude Code Handoff Protocol
**HCI AI Operating System — AI Team Operating Agreement**
**Version:** 1.0 | **Effective:** 2026-06-28
**Authored by:** Claude Code + Buck Adams (Owner)
**Ratified by:** Buck Adams (required before binding)

---

## Purpose

This document defines exactly how ChatGPT (GBT / Chief Architect) and Claude Code (Lead Implementation Engineer) collaborate. The goal: GBT's decisions become implementations without Buck having to manually relay every instruction.

---

## Current Architecture

```
Buck Adams (Owner / Final Authority)
        │
        ├── ChatGPT (GBT) — Chief Architect, Architecture Review Board
        │        │
        │        │  reads via ─────────────────────────────────────────┐
        │        │  Gateway Bridge (ngrok HTTPS)                       │
        │        │  Base: speculate-armband-retinal.ngrok-free.dev     │
        │        │  Auth: X-API-Key on write endpoints                 │
        │        │                                                     │
        │        │  writes via ─────────────────────────────────────── │
        │        │  POST /gateway/agent/handoff                        │
        │        │        ↓                                            │
        │        │  Architecture/Agent_Handoff/Inbox/                  │
        │        │        ↓                                            │
        │        │  handoff_processor.py → routes to Claude Code       │
        │        │                                                     ▼
        └── Claude Code — Lead Implementation Engineer         HCI AI OS DB
                 │                                             (hci_os)
                 │  reads / writes local filesystem
                 │  reads / writes DB via Docker
                 │  pushes to GitHub main
```

---

## What GBT Can Do Right Now (No Buck Required)

| Action | How | Endpoint |
|---|---|---|
| Read full system state | GET /gateway/project-state | No auth |
| Read any project brain | GET /gateway/project/{code}/brain | No auth |
| Read schedule status | GET /gateway/project/{code}/schedule | No auth |
| Read PM console | GET /gateway/project/{code}/pm | No auth |
| Read executive report | GET /gateway/executive/report | No auth |
| Vendor lookup | GET /gateway/knowledge/vendor?name=X | No auth |
| Search Drive | GET /gateway/drive/search?q=X | No auth |
| **Send Claude Code a task** | POST /gateway/agent/handoff | X-API-Key required |

---

## The Handoff Protocol (How GBT Talks to Claude Code)

### Step 1 — GBT writes a handoff

```http
POST https://speculate-armband-retinal.ngrok-free.dev/gateway/agent/handoff
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
Content-Type: application/json

{
  "title": "Short title for what needs to be built",
  "body": "Full description: what to build, why, any constraints or decisions made",
  "priority": "high | medium | low",
  "source": "chief_architect",
  "sop_references": ["SOP-14", "BP-15"],
  "acr_number": "ACR-005"  (optional — if this is an Architecture Review)
}
```

The gateway writes a `.md` file to `Architecture/Agent_Handoff/Inbox/`.

### Step 2 — Claude Code picks it up

**Current behavior (manual pickup):** Buck opens a Claude Code session and mentions the handoff. Claude Code reads the Inbox and executes.

**Target behavior (session pickup):** At the start of every Claude Code session, Claude Code checks:
```
Architecture/Agent_Handoff/Inbox/*.md
```
and processes any pending handoffs from GBT before taking other work.

### Step 3 — Claude Code responds

After implementation, Claude Code:
1. Commits the work with a descriptive message
2. Moves the handoff file from `Inbox/` → `Processed/` with a result note
3. Updates `LIVE_PROJECT_STATE.md`
4. Sends an ntfy notification on `hci-executive`

GBT reads the result via `/gateway/project-state` or GitHub raw.

---

## Formal Division of Labor

| Decision Type | Owner | Notes |
|---|---|---|
| Architecture decisions (schema, API design, service structure) | GBT (Chief Architect) | Files as ACR, Claude Code implements |
| Implementation details (code, SQL, config) | Claude Code | Within architecture constraints |
| Business rule changes (SOP, process, approval gates) | Buck Adams | Neither AI changes these without Buck |
| Production writes (HubSpot, email sends, contracts) | Buck Adams | Always requires explicit Buck approval |
| Git commits to main | Claude Code | Standard work |
| Git push to remote | Buck approves | Always confirm before push |

---

## What GBT Should Send vs. What It Should Not

### SEND via handoff:
- "Build endpoint X that does Y" (implementation request)
- "The schema for table Z should be changed to include column W" (ACR)
- "Wire up workflow A to call endpoint B" (integration task)
- "The SOP-15 compliance gap needs to be closed" (gap closure)

### Do NOT send via handoff (requires Buck directly):
- Anything that writes to HubSpot production
- Anything that sends external email
- Anything that modifies contract or legal documents
- Any financial approval or commitment
- Any decision that requires Buck's judgment about project priorities

---

## What Claude Code Should Do at Session Start

**Every session, before taking new work:**

1. Check `Architecture/Agent_Handoff/Inbox/` for pending GBT handoffs
2. Check `LIVE_PROJECT_STATE.md` for open items
3. Check `architecture/CHANGELOG.md` for last state
4. Then proceed with Buck's current request or next queued BTW

This means Buck never needs to say "check what GBT left" — Claude Code does it automatically.

---

## SOP Alignment Check (Required for Every Build)

Before implementing any feature, Claude Code verifies:

1. **Does a Business Process (BP-XX) govern this?** → Check `business_processes` table
2. **Is there an approval gate required?** → Check `sop_approval_gates` table
3. **Does the implementation follow the SOP's required inputs/outputs?** → Check `sop_inputs` and `sop_outputs` tables
4. **Should this require human approval before production write?** → Default YES for any data that leaves the system

If no BP governs the feature: flag it. Either it's infrastructure (OK) or a missing SOP definition (needs GBT review).

---

## Current Gateway Status

| Service | Status | Verified |
|---|---|---|
| ngrok tunnel | 🟢 LIVE | 2026-06-28 |
| /gateway/health | 🟢 ok, 76ms | 2026-06-28 |
| /gateway/project/{code}/brain | 🟢 LIVE | 2026-06-28 |
| /gateway/executive/report | 🟢 LIVE | 2026-06-28 |
| POST /gateway/agent/handoff | 🟢 LIVE — writes to Inbox | 2026-06-28 |
| /gateway/project/{code}/schedule | 🟢 LIVE — all 3 projects | 2026-06-28 |

**Note on ngrok URL:** The free ngrok URL (`speculate-armband-retinal.ngrok-free.dev`) is persistent but requires the local ngrok process to be running. If GBT gets a connection error, Buck needs to restart ngrok. A paid ngrok static domain would eliminate this dependency.

---

## Open Items on the GBT ↔ Claude Code Connection

| Item | Status | Owner |
|---|---|---|
| Auto-read Inbox at session start | Protocol defined here — not yet implemented in Claude Code habit | Claude Code |
| GBT ratifies this protocol | Needs GBT to read and acknowledge | GBT via /gateway/agent/handoff |
| Static ngrok domain | Optional but removes restart risk | Buck (paid ngrok plan) |
| Sprint 2 ACR from GBT | GBT needs to send Sprint 2 architecture direction | GBT |

---

## Revision History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-06-28 | Initial protocol — Claude Code authored, pending Buck + GBT ratification |
