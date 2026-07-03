# Approval Policy Registry
## HCI AI Operating System

**Authority:** Chief Architect Directive — Phase II (Objective 9)  
**Owner:** Buck Adams (HCI-AI Owner; PM & Superintendent at Hendrickson Construction)  
**Enforced by:** base_miner.py, all ingestion services, n8n gate workflows

---

## Policy Levels

| Level | Name | Who Decides | Speed | Examples |
|---|---|---|---|---|
| **AUTO** | Automatic | System — no human needed | Instant | Docs, reports, monitoring |
| **LOW** | Low-touch | Agent may proceed with logging | Same session | Vendor imports, dry-run |
| **MEDIUM** | Review | Queue for Buck — 24h default | Next session | Workflow activation, schema changes |
| **OWNER** | Owner decision | Buck Adams explicitly | His timeline | Contracts, financials, client comms |

---

## AUTO — Fully Autonomous (No Approval)

These actions are always safe and reversible. Agents execute immediately.

| Action | Why AUTO |
|---|---|
| Create/update documentation (.md files) | No business impact |
| Generate reports | Read-only output |
| Run health checks | Read-only monitoring |
| Run tests | No writes |
| Update LIVE_PROJECT_STATE.md | State reflection only |
| Update MISSION_QUEUE.md | Coordination file |
| Update EXECUTIVE_INBOX.md | Curation only |
| Update TASKS.md / CURRENT_SPRINT.md | Sprint tracking |
| Update AI_TEAM/ files | Agent coordination |
| Commit to git (local) | Reversible, not pushed |
| Rotate API keys | Security — auto-fix |
| Run miners (dry_run=True) | No writes |
| Scan for security issues | Read-only |
| Backup files before deletion | Protective action |
| Regenerate architecture diagrams | Documentation |
| Mining validation report | Read-only analysis |
| Session startup reads | Read-only |

---

## LOW — Low-Touch (Agent Proceeds, Logs Decision)

Agent can proceed without asking Buck, but records the decision for review.

| Action | Log to | Reversible? |
|---|---|---|
| Import vendor candidates to background_learning | mining_runs | Yes — BL records only |
| Dry-run mining with explicit dry_run=True | mining_runs | N/A — no writes |
| Workflow validation (test webhook with dummy payload) | n8n logs | Yes |
| Add records to background_learning_records | DB | Yes — status: Discovered only |
| Update integration_registry health check fields | DB | Yes |
| Create new n8n workflow (inactive) | n8n | Yes — not active |
| Schema migrations (additive only — ADD COLUMN, CREATE TABLE) | DB + migration log | Yes (IF NOT EXISTS) |
| Deploy new FastAPI endpoint (no external writes) | git commit | Yes |
| Register new integration (integration_registry) | DB | Yes |

---

## MEDIUM — Requires Queue + Buck Review

Agent queues item to `approval_queue`. Buck sees it in `EXECUTIVE_INBOX.md`. Agent waits before executing.

| Action | Gate | Queue Priority |
|---|---|---|
| Activate n8n workflow (makes it live) | AUTO-011 | medium |
| Deploy schema migration (destructive: DROP, ALTER type) | Architecture review | high |
| Deploy new connector (new external integration) | Architecture review | high |
| Merge vendor registry duplicates | Vendor gate | medium |
| Write bid import to DB | Bid gate | medium |
| Import Houzz data to houzz_* tables | Houzz gate | medium |
| Update project registry fields | Registry gate | medium |
| Upload file to Google Drive | Drive gate | medium |
| Run miner with dry_run=False (first time for a miner) | Mining gate | high |
| Push code to GitHub remote | Code gate | medium |
| Configure new launchd service | Infrastructure | medium |

---

## OWNER — Buck Decides (Never Automated)

These actions are permanently gated. No amount of confidence score bypasses them.

| Action | Gate | Why OWNER |
|---|---|---|
| **Write to HubSpot** | Gate H | Client data integrity |
| **Send email via Outlook** | Gate E | External commitment |
| **Contract approval** | Gate F | Legal + financial |
| **Budget approval** | Gate F | Financial authority |
| **Award bid to subcontractor** | Gate F | Financial commitment |
| **Invoice approval** | Gate F | Financial authority |
| **Change order approval** | Gate F | Contract modification |
| **Client communication** | Gate E | External commitment |
| **Production go-live** | Go-live gate | System integrity |
| **Enable mining dry_run=False (all miners)** | Mining gate | Data integrity |
| **Archive or delete project** | Governance | Irreversible |
| **Governance exception** | Constitution | Policy change |
| **New user / API key creation for external parties** | Security | Access control |

---

## How Agents Use This Registry

**Claude Code:** Before executing any action, classify it using this registry:
```python
# Example classification check
if action_type in AUTO_ACTIONS:
    execute_immediately()
elif action_type in LOW_ACTIONS:
    execute_with_logging()
elif action_type in MEDIUM_ACTIONS:
    queue_for_approval(priority="medium")
else:  # OWNER
    queue_for_approval(priority="high")
    add_to_executive_inbox()
```

**Mining Engine:** All miners use the base_miner.py classification:
- Records discovered → AUTO
- Vendor candidates → LOW (background_learning) → MEDIUM (registry write)
- Client data changes → OWNER (approval_queue, Gate H)

**n8n:** Gate workflows route by action type:
- AUTO → execute immediately
- LOW/MEDIUM → `approval_queue` insert + email Buck
- OWNER → `approval_queue` insert + email + block until approved

---

## Executive Inbox Format (Objective 3)

Every OWNER-level item in the Executive Inbox must contain:

```
**Decision:** [One sentence — what exactly will happen if approved]

**Recommendation:** [Approve / Reject / Defer] — [one sentence why]
**Confidence:** [High / Medium / Low] — [why this confidence level]
**Business Impact:** [What changes if approved; what's lost if rejected]
**Risk:** [What could go wrong; likelihood; mitigated by what]
**Deadline:** [Date or "No deadline" or "Gate 5: 2026-07-01"]

**Buck's response:** [ ] Approve  [ ] Reject  [ ] Defer  [ ] Modify: ___
```

No raw logs. No code. No implementation details. Owner-level context only.

---

## Approval Policy Enforcement (Future Sprint 4)

The policy registry will be embedded in code:
- `base_miner.py`: `classify_action(action_type)` → returns policy level
- `approval_queue` table: `policy_level` column added
- `EXECUTIVE_INBOX.md` auto-generation: only OWNER + unresolved MEDIUM items
- n8n AUTO-001: clears resolved items from inbox automatically

---

*Approval Policy Registry | HCI AI Operating System | Hendrickson Construction, Inc.*  
*v1.0 — 2026-06-27 | Enforced in base_miner.py, n8n gates, and agent directives.*
