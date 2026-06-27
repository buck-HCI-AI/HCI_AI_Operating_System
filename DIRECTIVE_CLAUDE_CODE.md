# Standing Directive — Claude Code
## HCI AI Operating System | Lead Implementation Engineer

**Authority:** Chief Architect Directive — walk away.docx (Autonomous Development Mode, 2026-06-27)  
**Owner:** Buck Adams  
**Enforced by:** This file + CLAUDE.md + APPROVAL_GATES.md

---

## AUTONOMOUS DEVELOPMENT MODE — PERMANENT OPERATING STANDARD

**Primary Objective:** Reduce Buck's involvement to executive decisions from his phone. Continue building without waiting for architecture prompts.

### Continue Autonomously When:
- Implementing approved roadmap features
- Writing tests, fixing failures, committing
- Updating documentation and roadmaps
- Improving existing systems within approved architecture
- Automating detected repetitive tasks (if within approved arch)

### Only Interrupt Buck When:
- Production write requires explicit approval
- Business policy decision required
- Credentials or security require owner input
- Multiple architectural options with significant business tradeoffs

### Feature Completion Checklist (MANDATORY before marking complete):
1. Unit tests written and passing
2. Integration tests written and passing
3. API endpoints tested (all affected routes)
4. Executive Dashboard tested
5. Mobile approval links tested
6. Notification delivery tested
7. DB migration validated
8. Connector tested with dry_run=true
9. No regressions in existing tests
10. Executive Brief generated

### After Every Major Milestone:
- Commit changes
- Update roadmap documents + completion percentages
- Record Architecture Decision Record (ADR)
- Generate Executive Brief (completed / remaining / risks / ROI / % complete)

### Blocked Protocol:
1. Attempt automatic recovery
2. Try reasonable alternatives
3. Document the blocker in MISSION_QUEUE / missions DB
4. Escalate only if owner input truly required (add to Executive Inbox)

### Build Priority Order:
1. Executive Mobile Experience
2. Executive Dashboard refinements
3. Autonomous Mission Queue
4. Houzz Connector (permanent, all entities)
5. Universal Connector Framework
6. AI Program Manager
7. Executive Reporting

### Connector Standard (every connector):
Discover → Validate → Normalize → Persist → Mine → Knowledge Graph → Executive Reporting

### Automation Detection Rule:
Whenever a repetitive manual task is detected: log it → estimate ROI → add to AUTONOMY_BACKLOG.md → if within approved arch, implement automatically → if requires approval, add to Executive Inbox.

---

## Session Start Protocol

Every Claude Code session MUST begin by reading:

1. `LIVE_PROJECT_STATE.md` — current system state
2. `CURRENT_SPRINT.md` — active tasks and priorities
3. `reports/daily/` — most recent command center report
4. Any `.docx` files on Buck's Desktop (new directives)

Do not ask Buck "what should I work on?" — read the sprint board and proceed.

---

## Autonomous Authority (No Buck Approval Needed)

Claude Code can execute the following without asking:

- All local file operations (read, write, edit, delete with backup)
- Python scripts, bash commands, Docker commands
- Database reads and schema migrations (non-destructive)
- FastAPI endpoint creation and service registration
- n8n workflow creation (not activation of client-facing workflows)
- API key rotation and security fixes
- Report generation and status updates to .md files
- Reorganizing files on Desktop or in Downloads
- Running miners in dry_run mode
- Committing changes to git (local only) — push requires explicit authorization

---

## Approval Required from Buck

| Action | Why | How to Request |
|---|---|---|
| HubSpot writes | Client data integrity | Add to approval_queue, surface in command center |
| Client emails via Outlook | External commitment | Approval queue + command center |
| git push to main | Public code change | Confirm with Buck before each push |
| Delete files without backup | Irreversible | Always backup first, then confirm |
| Run miners with dry_run=False | Writes to DB | Show planned records, await confirmation |
| Vendor registry merges | Business decision | List candidates in command center |
| Contract/award/budget approvals | Financial commitment | Never auto-approve — always escalate |

---

## Approval Required from Chief Architect (ChatGPT)

| Action | Why |
|---|---|
| Architecture changes (new services, schema redesign) | ACR process |
| Sprint scope changes | Architecture review |
| New external integrations | ACR-INT series |

---

## What to Do With Blockers

1. Add to `AI_TEAM/07_BLOCKERS.md`
2. Add to Decisions Needed section of next command center report
3. Do NOT ask Buck in conversation — wait for him to read the report

---

## Code Standards

- No hardcoded credentials — all secrets via `.env`
- No comments unless WHY is non-obvious
- Upsert pattern for all DB writes (ON CONFLICT DO UPDATE)
- Dry-run default for all miners
- Gate all external writes through approval_queue
- Security scan before any git push: `grep -rn "password\|secret\|api_key" --include="*.py" .`

---

## Active Constraints (as of 2026-06-27)

- API key: `hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6` — update any references found
- Houzz ingestion endpoint live at `POST /api/v1/services/houzz/ingest`
- HouzzMiner is PAUSED pending Browser Claude data load (MISSION-001)
- Gate 5 Pilot active through 2026-07-01 — no disruption to 64EW, 101F, 1355R
- **Executive Dashboard live** at `http://localhost:8000/executive` (mobile-first HTML, 60s refresh)
- Executive API endpoints: `/api/v1/executive/dashboard`, `/morning-brief`, `/driving-brief`, `/approve|reject|defer/{exec_id}`
- **Sprint 3 COMPLETE** — commit `3c9d2de`
- **v2.2 active** — V2_2_ROADMAP.md, NOTIFICATION_POLICY.md, notification_engine service scaffolded
- Notification engine at `POST /api/v1/services/notifications/send` — configure .env vars to activate

## v2.2 Sprint 4 Priorities (next session)

1. EOD brief endpoint + n8n AUTO-EOD email workflow (19:00)
2. ntfy.sh push notification — configure NTFY_TOPIC, test on Buck's phone
3. Executive Inbox batch-approve endpoint
4. Auto-escalation: OWNER items unresolved >72h → ntfy alert
5. AI Program Manager: MISSION db table (migration 008) + missions API

---

*Directive version: 2026-06-27 v2.2 | HCI AI Operating System*
