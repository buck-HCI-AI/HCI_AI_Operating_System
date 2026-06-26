# Duplicate Risk Report
Generated: 2026-06-26

This report identifies where duplication exists NOW within this repository and where risk of duplication will emerge when the Program Repository is introduced.

---

## HIGH RISK — Confirmed Duplicates (Fix Before Merge)

### 1. Unversioned API Routes
**Risk:** The FastAPI app exposes both `/api/v1/*` and unversioned `/bids/`, `/projects/`, `/vendors/`, `/workflows/*` routes. These are structural duplicates of the versioned routes.
**Impact:** External tools, n8n, or the MCP server calling the wrong prefix will get inconsistent behavior.
**Fix:** Remove unversioned route includes from `api/main.py` or redirect them to `/api/v1/`.

### 2. n8n Archived Workflows Not Deleted
**Risk:** 5 archived/retired workflows still exist in n8n (INACTIVE). Labels are correct ("ARCHIVED", "RETIRED") but they're not purged.
**Impact:** Future operators may activate them. Confusion during Program Repo governance review.
**Fix:** Delete after architecture review confirms no rollback needed.

### 3. AI_TEAM/ Documentation vs Future LIVE_PROJECT_STATE.md
**Risk:** AI_TEAM/ has 9 coordination documents covering status, roadmap, active work, decisions, architecture, backlog, next session, blockers, changelog. The Program Repository will introduce a `LIVE_PROJECT_STATE.md` as the controlling document.
**Impact:** Two sources of truth for the same information. Claude Code, Browser Claude, and ChatGPT will diverge on which to trust.
**Fix:** After `LIVE_PROJECT_STATE.md` is created in Program Repo, deprecate AI_TEAM/00–07 and redirect to it. Keep 08_CHANGELOG.md as implementation-only log.

### 4. infrastructure/ Has Two docker-compose Files
**Risk:** `infrastructure/docker-compose.yml` and `infrastructure/docker-compose.storage.yml` both exist alongside the root `docker-compose.yml`.
**Impact:** Unclear which is the authoritative startup file.
**Fix:** Confirm root `docker-compose.yml` is the live one; archive or delete infrastructure/ copies.

---

## MEDIUM RISK — Potential Duplicates With Program Repository

### 5. SOPs Defined in Two Places
**Risk:** This implementation repo has 27 SOPs defined in code (sop_execution/), registered in the API (`/api/v1/sop/registry`), and seeded into `business_processes`. The Program Repository likely contains SOP governance documents.
**Impact:** SOP definitions may diverge — code SOP vs governance SOP.
**Fix:** Program Repo SOPs are canonical text; implementation repo SOPs are executable versions. Keep both but enforce that code SOPs reference governance SOP version numbers.

### 6. Roadmap / Backlog
**Risk:** `AI_TEAM/01_ROADMAP.md` and `AI_TEAM/05_BACKLOG.md` exist here. Program Repo will own sprint planning and roadmap.
**Impact:** Buck or AI team members tracking tasks in the wrong place.
**Fix:** After handoff, mark AI_TEAM/01 and 05 as ARCHIVED with pointer to Program Repo.

### 7. Houzz Intelligence Design
**Risk:** Browser Claude has completed a Houzz Browser Intelligence design in Program Repo. This repo has `sync_houzz.py` and `houzz_projects` / `houzz_daily_logs` / `houzz_schedule_items` DB tables already implemented.
**Impact:** Parallel Houzz implementations may conflict.
**Fix:** Architecture review must reconcile Browser Claude's design with existing implementation before either advances.

### 8. Python Workflows vs n8n Workflows
**Risk:** `workflows/wf001–006` are Python implementations of the same WF-001–006 that exist in n8n. They can trigger each other or run independently.
**Impact:** A workflow could fire twice (once via n8n trigger, once via direct Python call).
**Fix:** Define clear separation: n8n is the scheduler/trigger layer; Python files are the execution layer called by n8n. Document this explicitly in CLAUDE.md.

---

## LOW RISK — Watch List

### 9. Multiple HCI_Project_Registry and HCI_Vendor_Registry Copies in Drive
**Risk:** Buck AI Drive folder contains 3 HCI_Project_Registry copies and 2 HCI_Vendor_Registry copies.
**Impact:** Reports may pull from stale copies.
**Status:** Registry workbook deduplicated (03 Registries is sole active copy). Others are likely orphaned.
**Fix:** Confirm via Drive API that orphaned copies are not referenced, then trash.

### 10. MCP Server vs Direct API Calls
**Risk:** Claude (this session) and MCP Server both call `http://localhost:8000`. The MCP server is a proxy over the API.
**Impact:** Not a true duplicate — they serve different caller contexts. But if the MCP server adds its own logic, drift can occur.
**Fix:** Keep MCP server as thin proxy only. No business logic in `hci_mcp_server.py`.

---

## Summary Matrix

| Item | Severity | Resolution Owner | Timing |
|---|---|---|---|
| Unversioned API routes | HIGH | Claude Code | Before pilot go-live |
| n8n archived not deleted | HIGH | Claude Code (with Buck confirm) | Before merge |
| AI_TEAM/ vs LIVE_PROJECT_STATE | HIGH | Architecture review | Post Program Repo setup |
| Infrastructure compose files | MEDIUM | Claude Code | Before merge |
| SOPs in two repos | MEDIUM | Architecture review | Post merge planning |
| Roadmap/backlog duplication | MEDIUM | Program Repo | Post merge |
| Houzz double implementation | MEDIUM | Architecture review | Before Houzz work restarts |
| Python WF vs n8n WF | MEDIUM | Claude Code (document) | Before pilot go-live |
| Drive Registry orphans | LOW | Claude Code (with Buck confirm) | P2 |
| MCP drift risk | LOW | Engineering standard | Ongoing |
