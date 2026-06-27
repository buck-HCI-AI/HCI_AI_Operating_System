# Standing Directive — Claude Code
## HCI AI Operating System | Lead Implementation Engineer

**Authority:** Chief Architect Directive — Reduce Buck Inputs (2026-06-27)  
**Owner:** Buck Adams  
**Enforced by:** This file + CLAUDE.md + APPROVAL_GATES.md

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

- API key rotated to `hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6` — update any references found
- Houzz ingestion endpoint live at `POST /api/v1/services/houzz/ingest`
- HouzzMiner is PAUSED pending Browser Claude data load
- Gate 5 Pilot active through 2026-07-01 — no disruption to 64EW, 101F, 1355R services

---

*Directive version: 2026-06-27 | HCI AI Operating System*
