# Integration Recommendations
Generated: 2026-06-26 | Audience: ChatGPT Chief Architect + Architecture Review

---

## Proposed Architecture

```
Program Repository (Governance Layer)
├── LIVE_PROJECT_STATE.md          ← single controlling document
├── Roadmap / Sprint Plans
├── SOP Governance Docs
├── Architecture Standards
├── Houzz Browser Intelligence Design
└── Cross-AI Coordination Files

Implementation Repository (Execution Layer)  ← THIS REPO
├── 03_Source_Code/                ← FastAPI + services + SOPs (executable)
├── docker-compose.yml             ← live infrastructure
├── AI_TEAM/                       ← deprecated after LIVE_PROJECT_STATE.md exists
├── 05_Database/                   ← schema + migrations
└── CLAUDE.md                      ← Claude Code operating rules
```

---

## Recommendation 1 — LIVE_PROJECT_STATE.md as Single Source of Truth

**Create in Program Repo.** This file should contain:
- Current sprint / active tasks
- Which AI is doing what
- System live state (what's running, what's broken)
- Approval-pending items
- Next session priorities

**Implementation Repo contract:**
- Claude Code reads LIVE_PROJECT_STATE.md at session start
- Claude Code writes to AI_TEAM/08_CHANGELOG.md (implementation log only)
- All other AI_TEAM/ docs are deprecated and pointer-redirected

**Transition path:**
1. ChatGPT creates LIVE_PROJECT_STATE.md in Program Repo
2. Claude Code archives AI_TEAM/00–07 with a redirect note
3. CLAUDE.md updated to reference Program Repo path

---

## Recommendation 2 — Houzz Reconciliation Before Restart

**Do not extend Houzz work in either repo until architecture review.**

Current state in this repo:
- `sync_houzz.py` — reads Houzz project data via web scraping
- DB tables: `houzz_projects`, `houzz_daily_logs`, `houzz_schedule_items`
- API: no dedicated Houzz service endpoint (sync only via `/workflows/sync/houzz`)

Browser Claude's design should be reviewed against this to determine:
- Does the Browser Intelligence design replace `sync_houzz.py`?
- Should DB tables be extended or replaced?
- Which triggers the Houzz read: n8n WF, MCP tool, or browser agent?

**Recommendation:** Browser Claude's design becomes the execution spec. Claude Code refactors `sync_houzz.py` to match it. Existing DB tables are preserved and extended.

---

## Recommendation 3 — Unversioned Route Removal

**Claude Code can execute this immediately without architecture review.**

Remove the unversioned route mounts from `api/main.py` (lines that include `/bids/`, `/projects/`, `/vendors/` etc. without the `/api/v1` prefix). This eliminates the highest-severity duplicate risk and has no functional impact since no live integrations use the unversioned paths.

---

## Recommendation 4 — n8n WF-008/009/010 Test Gate

**Before any new n8n development, test these three workflows in staging.**

- WF-008 Bid Follow-Up Engine — INACTIVE, not validated
- WF-009 New Job Setup — INACTIVE, not validated
- WF-010 Outlook Email Router — INACTIVE, not validated (HubSpot connected inbox not yet set up)

These should be validated against the 3 Gate 5 pilot projects before the pilot closes on 2026-07-01.

---

## Recommendation 5 — MCP Server as Primary AI Entry Point

The MCP server (`hci_mcp_server.py`, :8080) should become the **only** way external AI tools (Browser Claude, ChatGPT, future agents) access the HCI OS. Direct API calls from AI tools outside Claude Code should be deprecated in favor of MCP tool calls.

This enforces:
- Single audit trail (MCP calls are logged)
- Consistent credential handling (API key only in MCP layer)
- Tool definitions as the integration contract (not raw HTTP endpoints)

**Action:** Expose all major capabilities as MCP tools. Current tools cover 80% of use cases; add `GetVendorBenchmark`, `LogDecision`, `GetApprovalQueue` in next sprint.

---

## Recommendation 6 — Merge Sequence (When Ready)

If a formal repository merge is approved, suggested sequence:

1. **Architecture review** — ChatGPT reviews IMPLEMENTATION_INVENTORY.md + DUPLICATE_RISK_REPORT.md
2. **LIVE_PROJECT_STATE.md** created in Program Repo
3. **AI_TEAM/ deprecated** in Implementation Repo
4. **Unversioned routes removed** from FastAPI
5. **Houzz reconciliation** completed
6. **WF-008/009/010** tested
7. **Program Repo governance docs** linked from CLAUDE.md
8. **Gate 5 Pilot** closed with results captured
9. **Merge PR** reviewed by ChatGPT + Buck before merge

---

## What Claude Code Will NOT Do Without Architecture Approval

- Begin Houzz Browser Intelligence implementation
- Merge or reorganize the repository structure
- Create new DB tables beyond P1 scope
- Push any branch to remote
- Activate WF-008/009/010 without test results
