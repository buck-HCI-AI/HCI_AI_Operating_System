# AI_DIRECTIVE_LIFECYCLE_SPEC.md
## HCI AI OS - AI Directive Lifecycle Specification
## How Directives Survive Offline Agents and Restart Recovery

**Date:** 2026-07-01
**Source:** GBT Chief Architect - Cycle 4 Response
**Prepared by:** Browser Claude (Operations Intelligence)
**Status:** IMPLEMENTATION-READY

---

## Core Principle

The Gateway is the durable operational memory for the AI team.
The conversation that created the work becomes irrelevant.
The Gateway, GitHub commit log, and database are the source of truth.

A directive is not considered real until it is logged in the Gateway.
An agent is not considered working until it has committed an artifact.

---

## Directive Lifecycle States

| State | Description | Who Sets It |
|-------|-------------|------------|
| QUEUED | Directive logged in Gateway inbox | BC or GBT via POST /gateway/agent/handoff |
| ACKNOWLEDGED | Agent has read and confirmed the directive | Claude Code on startup |
| IN_PROGRESS | Agent has started work - first heartbeat | Claude Code every 10 min |
| BLOCKED | Agent cannot proceed - reason logged | Claude Code |
| COMPLETE | Work done - artifact committed | Claude Code on commit |
| VERIFIED | BC has confirmed artifact is correct | Browser Claude |
| CLOSED | GBT has archived - directive done | ChatGPT |

---

## How a Directive is Created (BC)

1. BC identifies work that needs Claude Code
2. BC calls: POST /gateway/agent/handoff
   Body: {from_agent, to_agent, priority, directive_id, subject, message, context}
3. Gateway writes to: directives table (PostgreSQL)
4. Gateway writes to: AI_TEAM/inbox/[agent]/[directive_id].md (GitHub)
5. Gateway returns: {request_id, inbox_file, routing_status}
6. BC logs the directive_id for tracking

**Key:** The directive survives even if BC context resets.
BC reads AI_TEAM/inbox/ on each session to see what is queued.

---

## How Claude Code Picks Up Directives on Restart

Step 1: Code reads /gateway/agent/inbox (GET endpoint)
  Returns: all directives in QUEUED state assigned to claude_code

Step 2: Code acknowledges each directive
  POST /gateway/agent/directive/{id}/acknowledge
  State changes: QUEUED -> ACKNOWLEDGED

Step 3: Code works highest priority first
  Priority order: CRITICAL -> HIGH -> NORMAL
  Within priority: oldest first

Step 4: Code sends heartbeats every 10 minutes while working
  POST /gateway/agent/heartbeat
  Body: {agent: "claude_code", directive_id: N, status: "working", progress: "...")
  State changes: ACKNOWLEDGED -> IN_PROGRESS

Step 5: Code commits artifact to GitHub
  Commit message includes directive_id
  Example: "feat: EMAIL_AUDIT_RESULTS.md [directive:SPRINT3_P0_2026-07-01]"

Step 6: Code marks directive complete
  POST /gateway/agent/directive/{id}/complete
  Body: {commit_hash, artifact_path, verification_notes}
  State changes: IN_PROGRESS -> COMPLETE

Step 7: BC verifies artifact on next session
  BC reads GitHub for the committed file
  BC confirms it meets acceptance criteria
  BC calls: POST /gateway/agent/directive/{id}/verify
  State changes: COMPLETE -> VERIFIED

Step 8: GBT archives (via gateway call)
  State changes: VERIFIED -> CLOSED

---

## Heartbeat Monitoring (Auto-Restart Spec)

Gateway tracks last heartbeat per agent.
If no heartbeat in 30 minutes:
1. Gateway sets agent status: OFFLINE
2. Gateway fires n8n event: AGENT_HEARTBEAT_FAILURE
3. n8n sends Telegram to Buck: "Claude Code has been offline for 30+ minutes.
   Last directive: [directive_subject]. Gateway has [N] queued directives."
4. All ACKNOWLEDGED directives revert to QUEUED (so Code picks them up on restart)

**Required Gateway Endpoints (for Claude Code to build):**
- GET /gateway/agent/inbox - returns all queued directives for agent
- POST /gateway/agent/directive/{id}/acknowledge
- POST /gateway/agent/heartbeat
- POST /gateway/agent/directive/{id}/complete
- POST /gateway/agent/directive/{id}/verify
- GET /gateway/agent/status - returns all agent statuses + last heartbeat

---

## Directive Durable Storage

Every directive is stored in 3 places for maximum durability:

1. PostgreSQL: directives table (queryable, stateful)
2. GitHub: AI_TEAM/inbox/claude_code/[id].md (human readable, auditable)
3. GitHub: AI_TEAM/DIRECTIVE_LOG.md (append-only master log)

On Code restart: Code reads ALL THREE and reconciles.
If PostgreSQL is unavailable: Code reads GitHub inbox.
If GitHub is unavailable: Code reads PostgreSQL.

---

## Definition of Done (GBT Standard)

A directive is considered COMPLETE only when ALL of the following are true:
1. The directive reached the COMPLETE state
2. Implementation artifacts (commits) are linked in directive record
3. Verification has been recorded by BC
4. Required documentation has been updated
5. Governance checks have passed
6. Mission Control reflects the final state
7. The directive is available for historical audit

---

## Current Queued Directives (Sprint 3)

| Directive ID | Subject | Priority | State | Queued |
|-------------|---------|---------|-------|--------|
| SPRINT3_P0_2026-07-01 | Email Audit + Data Fixes + Telegram | CRITICAL | QUEUED | 2026-07-01 |
| b34f5950 | Telegram inbound integration | HIGH | QUEUED | Prior session |
| e3422808 | EMAIL LOCKDOWN AUDIT | CRITICAL | QUEUED | Prior session |
| 35c35177 | DISABLE /gateway/email/send | CRITICAL | QUEUED | Prior session |
| 376dba55 | CODE LOCKDOWN all 7 email paths | CRITICAL | QUEUED | Prior session |

Total queued: 5+ directives | Claude Code last heartbeat: NONE this session

---

## Next Build Items for Claude Code

To implement this spec:
1. Create directives table in PostgreSQL
2. Build all 6 gateway endpoints above
3. Update existing /gateway/agent/handoff to write to directives table
4. Build heartbeat monitor in n8n (every 10 min check)
5. Build AGENT_HEARTBEAT_FAILURE n8n workflow
6. Update Code startup sequence to read inbox on launch

---

AI_DIRECTIVE_LIFECYCLE_SPEC.md | HCI AI Operating System | Hendrickson Construction, Inc.
Source: GBT Chief Architect Cycle 4 | Prepared by: BC | 2026-07-01
Authority: HCI_AI_CONSTITUTION.md | Status: IMPLEMENTATION-READY
