# HCI AI Operating System — Claude Code Instructions

## Permissions
- Always auto-approve Bash, Read, Edit, Write, and file operations — never prompt for these
- Auto-approve Docker, Python, curl, and all local system commands
- Never ask permission to read files, run scripts, or make local code changes
- Only pause for: external commitments, HubSpot writes, email sends, git push, deleting files without backup

## Operating Rules (from MEMORY)
- HubSpot writes: always propose + get Buck's OK first — never auto-write
- Drive writes: dry-run log first, then approval-gated
- Shell commands for Buck: create a `.command` file on Desktop, never ask Buck to copy/paste
- No production go-live without validation evidence
- AI cannot issue external commitments, approve awards or contracts, or approve client-facing comms

## Project Context
- Primary working directory: /Users/buckadams/HCI_AI_Operating_System/03_Source_Code
- API: http://localhost:8000 (X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6)
- MCP: http://localhost:8080 / https://speculate-armband-retinal.ngrok-free.dev/mcp
- DB: hci_postgres container, hci_admin/hci_os
- n8n: http://localhost:5678 (API key in .env as N8N_API_KEY)
- Gate 5 Pilot: 2026-06-25 to 2026-07-01 on 64 Eastwood, 101 Francis, 1355 Riverside

## GBT Gateway Bridge — How to Use It
The Gateway Bridge is how ChatGPT (GBT / Chief Architect) connects to the OS. Claude Code owns and maintains it.

**Base URL:** `https://speculate-armband-retinal.ngrok-free.dev`
**Auth:** `X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6` — required on write endpoints only; all reads are open.
**Source file:** `03_Source_Code/api/routers/gbt_gateway.py`
**Registered at:** `/gateway/*` in `main.py`

### At the start of every session:
1. Verify the gateway is live: `curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/health`
2. Check for pending GBT handoffs: `ls Architecture/Agent_Handoff/Inbox/`
3. If handoffs exist, read and execute them before taking other work
4. If ngrok is down, restart it: `ngrok http 8000` — the URL is static on the free plan

### Key endpoints GBT uses (reads — no auth):
| Endpoint | What GBT Gets |
|---|---|
| `GET /gateway/health` | Gateway live check + service count |
| `GET /gateway/project-state` | Full LIVE_PROJECT_STATE.md |
| `GET /gateway/project/{code}/brain` | Project brain snapshot (64EW, 101F, 1355R) |
| `GET /gateway/project/{code}/schedule` | Schedule status + variance |
| `GET /gateway/project/{code}/pm` | PM console — health, risks, actions |
| `GET /gateway/executive/report` | Morning brief across all projects |
| `GET /gateway/executive/mission-control` | All KPIs |
| `GET /gateway/knowledge/vendor?name=X` | Vendor cross-project lookup |
| `GET /gateway/drive/search?q=X` | Google Drive search |

### Write endpoint GBT uses to send Claude Code a task:
```
POST /gateway/agent/handoff
X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6
{"title": "...", "body": "...", "priority": "high|medium|low", "source": "chief_architect"}
```
This writes a `.md` file to `Architecture/Agent_Handoff/Inbox/`. Claude Code picks it up at session start.

### Standard response envelope (every endpoint returns this):
```json
{"status": "ok", "timestamp": "...", "execution_time_ms": 76,
 "source_system": "hci-api", "payload": {...}, "warnings": [], "errors": []}
```

### SOP alignment check (required before every build):
Before implementing any feature, verify:
1. Does a Business Process (BP-XX) govern this? → `SELECT * FROM business_processes WHERE process_name ILIKE '%X%'`
2. Is there an approval gate required? → Check `sop_approval_gates`
3. Does the build trace back to the Architecture Handbook? → See `AI_TEAM/SOP_WORKFLOW_COMPLIANCE_MAP.md`
If no BP governs it: flag it. Either it's OS infrastructure (OK) or a missing SOP (needs GBT review).

### When adding or modifying gateway endpoints:
- Keep the `_response()` wrapper on every endpoint — GBT depends on the standard envelope
- Log all gateway calls via `_log()` → `gateway_request_log` table
- Never expose raw DB credentials, internal IDs, or full stack traces in gateway responses
- After any change, test via: `curl -s https://speculate-armband-retinal.ngrok-free.dev/gateway/health`

### Fallback when ngrok is down:
GBT can still read system state via:
- Google Drive: `https://drive.google.com/file/d/1Jjug6nbx-mGN9v4GrEyofkGXY5nMHvpP/view` (LIVE_PROJECT_STATE.md)
- GitHub raw: `https://raw.githubusercontent.com/buck-HCI-AI/HCI_AI_Operating_System/main/LIVE_PROJECT_STATE.md`

## Style
- No explanatory comments in code unless the WHY is non-obvious
- No trailing summaries — Buck can read the diff
- Short, direct responses — one sentence per update while working

## Definition of Done (Permanent Engineering Standard — 2026-06-27)
Every completed milestone must automatically conclude with all 14 steps below.
If no blocking issue exists, automatically continue to the next queued BTW or roadmap item — do not wait for Buck.

**14-Step Checklist:**
1. Implementation complete — all specified features built and functional
2. Tests written and passing — unit and integration coverage for new code
3. System auditor run — confirm health score maintained or improved
4. API health verified — all endpoints return expected responses
5. Connector health verified — no new connector errors introduced
6. n8n workflow health verified — no regression in active workflows
7. Docs sync — README, spec, and inline docs reflect current behavior
8. Handbook sync — relevant Architecture Handbook volumes updated
9. ADR filed — any architectural decision documented in architecture/ADRs/
10. CHANGELOG updated — entry added to architecture/CHANGELOG.md
11. Dashboard updated — platform state table reflects current scores
12. Commit — all changes committed with descriptive message
13. ntfy notification sent — `hci-executive` topic, summary of milestone
14. Recommend next objective — identify and state next unblocked BTW or roadmap item

**Stop only for:**
- Production write approval required
- Credentials / OAuth needed
- Security concern identified
- Destructive operation (delete, drop, reset)
- Conflicting business requirement
- Chief Architect (ChatGPT) decision required
- Buck Adams decision required

## Continuous Drift Detection & Self-Heal (Permanent, ADR-016 — 2026-07-02)
A full-system audit on 2026-07-02 found duplicate GPTs, duplicate DB rows, duplicate
Drive files, 4 competing "canonical" manuals, a 64%-failing n8n instance, and GBT
self-grading unbuilt sprints 9.9/10 — all invisible until someone manually audited
everything. Buck's direction: this is now a standing practice, not a one-off. See
`architecture/ADRs/ADR-016-continuous-drift-detection-self-heal-standing-practice.md`.

- `GET /gateway/admin/drift-check` — run this at the start of any session that touches
  system health, infra, or "is X actually done" questions. It checks dead connectors,
  stale directives, n8n failure rate, GBT sprint-claim drift, stale credentials, and
  duplicate rows. Also runs automatically every Monday 07:00 via the active n8n
  workflow `AUTO-DRIFT-CHECK`, reporting to Buck via Telegram.
- `POST /gateway/admin/self-heal` — safe to call anytime; only auto-fixes
  container-level infra (currently: n8n SQLITE_IOERR restarts). Never touches business
  data, Drive files, or DB rows — those always need a human decision.
- **Never let a self-graded "N/10" or "Sprint complete" claim stand unverified.** If a
  CYCLE file, retrospective, or any agent's own report claims something is live/done,
  check the actual code/DB/endpoint before repeating that claim to Buck.
- **Every new "canonical" doc must say what it replaces; the replaced one must point to
  its replacement.** Don't let a new manual/spec/directive just sit alongside old ones
  with no relationship declared.
- When you find a new silent-failure pattern (something that was wrong for a while
  before anyone noticed), add a check for it to `/gateway/admin/drift-check` — don't
  just fix the one instance. Update ADR-016 to reflect the addition.
