# SYSTEM-WIDE OVERNIGHT DIRECTIVE
## HCI AI Operating System — All Agents

**Issued:** 2026-06-30
**Authority:** Buck Adams (HCI-AI Owner; PM & Superintendent at Hendrickson Construction)
**Issued by:** Browser Claude (Operations Intelligence) + HCI Chief Architect (GBT)
**Gateway Request ID:** 1ffc81be
**Status:** ACTIVE — all agents, work through the night

---

## Who This Applies To

| Agent | Role | Overnight Task |
|---|---|---|
| Claude Code | Lead Implementation Engineer | Phases 1-7 below |
| GBT (ChatGPT) | Chief Architect / ARB | Continue governance, review Phase 3 output, draft book chapter |
| Browser Claude | Operations Intelligence | Monitor GitHub commits, watch for blockers, report morning summary |
| n8n | Automation | Stay live, process any triggered workflows |

---

## Operating Mode — ALL AGENTS

Buck is offline. Work continuously. Do not stop. Do not wait for prompts.
Stop ONLY for: production safety issues, data loss risk, external communications requiring Buck authorization.
Default behavior: continue building, auditing, testing, improving.

---

## PHASE 1 — FULL SYSTEM AUDIT

**Owner: Claude Code**

- Read every file in AI_TEAM/ (all 20+ files)
- Read LIVE_PROJECT_STATE.md, CURRENT_SPRINT.md, 00_STATUS through 09_HANDOFF_PROTOCOL
- Cross-reference against live gateway state
- Answer definitively:
  - What did we lose in the shutdown?
  - What is missing vs what was live before restart?
  - What is stale / out of sync?
  - What is broken?
  - Are we at full capability?
- Document all findings in AI_TEAM/AUDIT_FINDINGS.md
- Commit: "audit: full system audit post-shutdown"

---

## PHASE 2 — SHUTDOWN RECOVERY

**Owner: Claude Code**

- Fix everything identified in Phase 1
- Restore full capabilities — nothing lost
- Close every gap between current state and pre-shutdown state
- Update all state files to reflect reality
- Commit: "recovery: post-shutdown gaps closed"

---

## PHASE 3 — LESSONS LEARNED

**Owner: Claude Code (draft) + GBT (review + book chapter)**

Claude Code writes AI_TEAM/LESSONS_LEARNED.md:
- What broke during the shutdown and why
- What the fix was
- What architectural change prevents recurrence
- How the system is stronger now than before

GBT reviews and expands into a book chapter:
- Chapter title: "Resilience by Design: What the Shutdown Taught Us"
- Audience: future HCI AI team members, construction industry AI adopters
- Content: the incident, the diagnosis, the fix, the architectural principle, the outcome
- Tone: confident, forward-looking, practical
- Format: ready to drop into the HCI AI OS Manual

---

## PHASE 4 — BECOME STRONGER (implement the fixes)

**Owner: Claude Code**

Build these in order — audit existing before creating new:

### 4a. ai_directives — Durable Directive Persistence
- Survives restart
- States: ISSUED / RECEIVED / IN_PROGRESS / COMPLETE / BLOCKED / REJECTED
- Gateway CRUD: POST create, POST acknowledge, PATCH status, GET list, GET by ID
- Any agent can query its own directive queue on startup
- Mission Control reflects directive state

### 4b. ai_heartbeat — Agent Registration
- All agents register heartbeat on startup
- Fields: agent_name, role, timestamp, status, current_task, last_directive_id
- POST /gateway/heartbeat endpoint
- BC can see which agents are live at any moment
- Stale heartbeat detection (60s threshold)
- Mission Control displays AI team health

### 4c. Warm Start Protocol — 60-Second Recovery
- Any agent reads GitHub AI_TEAM/ and is fully operational in under 60 seconds
- No dependency on another agent being live to recover
- Test it: simulate cold start, measure time to operational
- Document the protocol in 09_HANDOFF_PROTOCOL.md

### 4d. Overnight Directive Auto-Generation
- System generates OVERNIGHT_DIRECTIVE.md automatically at session end
- No manual BC intervention required
- n8n trigger: on session close event → generate + commit directive
- Gateway endpoint: POST /gateway/overnight/generate

### 4e. Plugin Spec Update
- Add POST /gateway/agent/handoff to OpenAPI plugin spec
- GBT calls it directly — BC no longer required as intermediary
- Schema: title, body, priority, source, sop_references (optional)

---

## PHASE 5 — FULL CAPABILITY VERIFICATION

**Owner: Claude Code**

Run full test suite. Verify every system:
- [ ] All 427 API endpoints respond
- [ ] Gateway health: green
- [ ] Mission Control: reflects reality
- [ ] Approval queue: operational
- [ ] Executive inbox: operational, no stale test data
- [ ] Knowledge graph: live
- [ ] Continuous discovery: live
- [ ] Approval loop: live
- [ ] Event bus: live
- [ ] n8n workflows: live
- [ ] ai_directives: ISSUED/RECEIVED/IN_PROGRESS/COMPLETE lifecycle verified
- [ ] ai_heartbeat: all agents registered
- [ ] Warm start: tested, under 60 seconds
- [ ] 101F variance: -5 days confirmed across all surfaces
- [ ] 1355R risks: 0 production risks confirmed

Document results in OVERNIGHT_REPORT.md.

---

## PHASE 6 — BUILD FOR THE FUTURE

**Owner: Claude Code (implement) + GBT (architecture decisions)**

After recovery and verification complete, keep building:

### Priority 1: AI Architecture Inbox
- Tracked ownership for every directive
- Acknowledgement required before status moves to IN_PROGRESS
- ARB review queue for architecture decisions

### Priority 2: Mission Control — Single Operational Dashboard
- Real-time: all agents, all projects, all risks, all directives
- No refresh required
- Buck sees everything in one view at localhost:8000/executive

### Priority 3: Unified Task Registry
- Every task has: owner, status, created_at, due_date, linked directive
- No orphan tasks
- Cross-agent visibility

### Priority 4: AI Memory Sync
- ChatGPT, Claude Code, Browser Claude all read from the same GitHub state
- Session start = pull latest AI_TEAM/ files
- Session end = commit state update

---

## PHASE 7 — MORNING REPORT

**Owner: Claude Code (commit) + GBT (executive summary) + BC (confirm)**

Write AI_TEAM/OVERNIGHT_REPORT.md:

1. Full capability status (green/yellow/red per system)
2. All work completed tonight (commits, files changed)
3. Test results
4. Lessons learned summary (3 bullet points)
5. What was built for the future
6. Items requiring Buck review
7. Recommended first action for Buck in the morning

Commit: "overnight: morning report — 2026-07-01"

---

## THE BOOK — HCI AI OS Manual

**Owner: GBT (Chief Architect)**

While Claude Code executes phases 1-7, GBT drafts the following book sections:

### Chapter: "Resilience by Design"
What the shutdown taught us. How the system came back stronger.

### Chapter: "The AI Operations Control Plane"
What we built. Why it matters for construction. How any HCI employee or AI agent can pick it up and run.

### Chapter: "The Continuous Engineering Organization"
How HCI shifted from feature development to a production engineering team that never stops improving.

Format all chapters as commit-ready markdown. BC will commit them to the repo when ready.

---

## Governance Rules (inviolable)

- Audit before building
- Extend existing before creating new
- No duplicate systems — one source of truth
- Do NOT write to HubSpot, send emails, submit bids, or make external commitments
- Do NOT delete real production data
- Buck approval required for: external comms, contracts, financial transactions
- All commits go to main branch with clear descriptive messages
- Every architectural decision gets recorded in 03_DECISIONS.md

---

*Gateway directives queued: 2a234787, edec1ecb, 1ffc81be*
*All prior overnight directives remain active and are incorporated here*
*This is the authoritative overnight work plan — supersedes OVERNIGHT_DIRECTIVE.md*
*Issued: 2026-06-30 by BC + GBT | Authority: Buck Adams*
