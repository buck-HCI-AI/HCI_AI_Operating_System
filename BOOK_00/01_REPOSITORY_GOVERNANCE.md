# BOOK_00 § 01 — Repository Governance and AI Collaboration

---

## Repository as Engineering Memory

The repository is the shared memory between Buck, Claude Code, and ChatGPT. Code, specs, decisions, status, and architecture all live here. Chat history is ephemeral. The repository is permanent.

**Location:** `/Users/buckadams/HCI_AI_Operating_System`  
**Remote:** `buck-HCI-AI/HCI_AI_Operating_System` (GitHub private)  
**Branch convention:** `feature/*` for builds; `main` for stable

---

## AI Team Division of Labor

| Assistant | Role | Does NOT |
|-----------|------|----------|
| **Claude Code** | Builder — writes code, edits files, runs terminal commands, builds and fixes | Design architecture, approve business decisions |
| **ChatGPT** | Architect — designs, documents, reviews, governs | Write code, touch files |
| **Buck** | Owner — approves business decisions, authorizes writes to external systems | Write code |

---

## Claude Code Operating Rules

1. **Just fix it** — if Claude can resolve something without Buck, do it. Only escalate when Buck's UI action or a business decision is required.
2. **Auto-read** — always read/access any resource reachable without Buck (Outlook, Drive, HubSpot, PDFs). Never ask permission to read.
3. **Never auto-write HubSpot** — always report proposed changes and ask permission first.
4. **No delete without backup + confirmation** — destructive operations require explicit approval.
5. **No commit without request** — create commits only when Buck asks.
6. **Desktop .command files** — for any shell command Buck needs to run, create a double-clickable `.command` file on the Desktop. Never ask Buck to copy/paste into Terminal.
7. **Architecture rule** — do not allow workflows to create private data models, storage paths, or prompt libraries. Use common services.

---

## Repository Structure

```
HCI_AI_Operating_System/
├── BOOK_00/                    ← Master specification (this book)
├── AI_TEAM/                    ← Live engineering state (Claude reads every session)
├── 01_Engineering_Library/     ← Source PDFs and governing documents
├── 03_Source_Code/
│   ├── api/                    ← FastAPI app (main.py, routers/, middleware/, services/)
│   ├── services/               ← 9 Construction Intelligence Services
│   ├── workflows/              ← Workflow Python implementations
│   ├── ingestion/              ← Document ingestion pipeline
│   ├── integrations/           ← HubSpot, Drive, Graph API clients
│   └── agents/                 ← Agent stubs (future)
├── 04_Workflows/               ← n8n JSON exports
├── 05_Database/                ← Legacy schema location (use database/ going forward)
├── 06_Project_Documentation/   ← Per-project README files
├── database/                   ← SQL schema files, migrations, seeds
├── docs/                       ← Technical documentation (inventory, sequence, overlap)
├── infrastructure/             ← Docker, scripts, drive setup
├── SESSION_STARTUP/            ← Per-session context for each AI assistant
└── workflows/                  ← Workflow markdown specs (superseded by BOOK_00)
```

---

## AI_TEAM Files (Claude reads at session start)

| File | Purpose |
|------|---------|
| `00_STATUS.md` | Current state of every component |
| `01_ROADMAP.md` | High-level phase plan |
| `02_ACTIVE_WORK.md` | What's in progress right now |
| `03_DECISIONS.md` | Architecture decisions made |
| `04_ARCHITECTURE.md` | Current system architecture |
| `05_BACKLOG.md` | All planned work not yet started |
| `06_NEXT_SESSION.md` | Exactly what to do next session |
| `07_BLOCKERS.md` | What is blocked and why |
| `08_CHANGELOG.md` | What was built, when |
| `09_HANDOFF_PROTOCOL.md` | How to hand off between sessions |

---

## Session Startup Protocol

**Claude Code session start:**
1. Read `AI_TEAM/00_STATUS.md`
2. Read `AI_TEAM/06_NEXT_SESSION.md`
3. Read the relevant BOOK_00 section for context
4. Do not re-derive what is already documented

**Session end (every session):**
1. Update `AI_TEAM/00_STATUS.md`
2. Update `AI_TEAM/06_NEXT_SESSION.md`
3. Update `AI_TEAM/08_CHANGELOG.md`
4. Update `BOOK_00/15_ROADMAP.md` if phase status changed
