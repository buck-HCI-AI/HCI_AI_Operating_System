# HCI Command Center
## Hendrickson Construction, Inc. — AI Operating System

**Last Generated:** Auto-updated daily at 07:00 by `scripts/generate_command_center.py`  
**Authority:** Chief Architect Directive — Reduce Buck Inputs (2026-06-27)

> **How to use this file:**
> Buck reads the **Decisions Needed** and **Blockers** sections. Everything else is handled by agents.
> The daily report lives at `reports/daily/YYYY-MM-DD-hci-command-center.md`.

---

## What Each Agent Handles Autonomously

| Agent | Does Automatically | Requires Buck Approval |
|---|---|---|
| **Claude Code** | Builds endpoints, fixes bugs, runs scripts, updates docs, rotates keys | HubSpot writes, git push, external commitments, contracts |
| **Browser Claude** | Governs GitHub repo, extracts Houzz data, posts to ingestion endpoint | Branch merges to main, external communications |
| **ChatGPT (Chief Architect)** | Issues ACRs, architectural directives, vendor strategy | Architecture changes that affect production |
| **n8n** | Runs all automated workflows, sends health reports, queues approvals | Any workflow that writes to HubSpot or sends client emails |
| **Mining Engine** | Scans HubSpot/Drive/Houzz/Outlook, extracts intelligence, queues vendors | Vendor merges, budget approvals, client-facing writes |

---

## Daily Operating Loop

```
07:00  n8n AUTO-001     → generates daily status report
06:00  n8n AUTO-002     → health check, alerts if service down  
08:00  n8n AUTO-003     → sprint self-status
03:00  n8n AUTO-004     → mining engine sweep (all 8 miners)
07:00  scripts/generate_command_center.py → THIS FILE's data
```

---

## Buck's Role (Reduced)

1. **Read:** `reports/daily/YYYY-MM-DD-hci-command-center.md` each morning
2. **Approve or defer** items in the Decisions Needed section
3. **Authorize** go-live when agents report ready
4. **Issue directives** via .docx on Desktop when you want architecture changes

**That's it.** Agents handle coordination, reporting, and execution.

---

## How to Issue a Directive

1. Write a .docx file and drop it on Desktop
2. Open a Claude Code session and paste the path: `/Users/buckadams/Downloads/Directive.docx`
3. Claude Code reads it and executes autonomously

---

## Key Links

| Resource | Path |
|---|---|
| **Executive Inbox** | `EXECUTIVE_INBOX.md` ← **Buck reads this daily** |
| **Step-away report** | `reports/BUCK_CAN_STEP_AWAY-2026-06-27.md` |
| Daily report | `reports/daily/YYYY-MM-DD-hci-command-center.md` |
| Active missions | `MISSION_QUEUE.md` |
| Agent coordination | `EVENT_BUS_ARCHITECTURE.md` |
| Operating model | `AUTONOMOUS_OPERATING_MODEL.md` |
| Agent directives | `DIRECTIVE_CLAUDE_CODE.md`, `DIRECTIVE_BROWSER_CLAUDE.md` |
| Live project state | `LIVE_PROJECT_STATE.md` |
| Current sprint | `CURRENT_SPRINT.md` |
| Task register | `TASKS.md` |
| Approval queue | `GET /api/v1/services/approval-queue/pending` |
| API docs | `http://localhost:8000/docs` |

---

## Generate Report Now

```bash
python3 scripts/generate_command_center.py
```

Or from a Claude Code session: just ask "generate today's command center report."

---

*HCI AI Operating System | Hendrickson Construction, Inc.*
*This file is the index. Daily reports are in reports/daily/.*
