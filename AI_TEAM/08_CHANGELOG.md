# 08_CHANGELOG.md
**Engineering changelog — what changed, when, and why**
Most recent first.

---

## 2026-06-24 — Session 2 (afternoon)

**Engineer:** Claude Code | **Architect:** ChatGPT (async via CHATGPT_BRIEFING.md)

### Added
- AI_TEAM/ directory — 9 files per Collaboration Proposal v1.0
- BOOK_00 canonical engineering manual seed (`00_Manuscripts/BOOK_00/00_MASTER.md`)
- `HCI_AI_Claude_Code_Operating_Charter_v0.1.pdf` → `01_Engineering_Library/`
- `HCI_AI_Repository_Collaboration_Proposal_v1.pdf` → `01_Engineering_Library/`
- `CHATGPT_BRIEFING.md` → `01_Engineering_Library/`

### Changed
- `.gitignore` — allow `01_Engineering_Library/*.pdf` and `09_PDFs/*.pdf`
- AI_TEAM file names migrated from descriptive names to numbered scheme (00–08)

### Decisions
- DEC-006: Claude Code Operating Charter v0.1 adopted
- DEC-007: Repository Collaboration Proposal v1.0 adopted (see 03_DECISIONS.md)

---

## 2026-06-24 — Session 2 (morning, repo init)

**Engineer:** Claude Code

### Added
- `HCI_AI_Operating_System/` git repository — initial structure (15 files, commit `be76e39`)
  - `.env.example`, `.gitignore`, `README.md`, `docker-compose.yml`
  - `03_Source_Code/integrations/` (credentials.py, hubspot.py, google_sheets.py, microsoft_graph.py)
  - `04_Workflows/WF-007_Bid_Leveling_Engine.json`
  - `05_Database/postgres/schema.sql`, `05_Database/qdrant/collections.md`
  - `06_Project_Documentation/` (64_Eastwood, 101_Francis, 1355_Riverside READMEs)
- `CHATGPT_BRIEFING.md` (commit `0bbc8e1`)
- GitHub CLI installed (`gh 2.95.0`)

### Changed
- Repo renamed from `HCI_OS` → `HCI_AI_Operating_System` (Constitution naming spec)

---

## 2026-06-24 — Session 1 (morning)

**Engineer:** Claude Code

### Operational Actions
- Tolteck masonry bid ($7,150) logged: 64EW Google Sheet row 14 updated (4 cells)
- HubSpot 64EW deal moved to Leveling stage; bid note added
- WF-007 bid leveling ran for 64EW and 101F; HTML reports built directly (n8n SQLITE_IOERR workaround)
- 101F bid request emails created (Pella Windows + CQ Roofing + Green Point + CO Highlands)
- All 4 emails logged as HubSpot engagements

### Fixed
- WF-007 Send Draft nodes: reference upstream `Level Bids` node to preserve html/projectName/dateStr after xlsx upload node wipes $json
- HubSpot auth: removed double `Bearer ` prefix (cred["value"] already includes it)

### Engineering Context
- n8n SQLITE_IOERR during WF-007 runs → worked around via direct Python + Google Sheets API
- HubSpot pipeline ID: `2203777729` | 7 stages mapped in hubspot.py
