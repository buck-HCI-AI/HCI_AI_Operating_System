# 05_BACKLOG.md
**All planned work not yet active — prioritized**
Last updated: 2026-06-26 (MVP Sprint 1 COMPLETE)

---

## ACTIVE — Gate 5 Pilot (2026-06-25 to 2026-07-01)

### Daily Operations (Buck — in progress)
- [ ] Use 6 MVP workflows daily on 3 pilot projects
- [ ] Review and action approval queue items
- [ ] Collect ROI evidence (minutes saved per workflow)
- [ ] At pilot end: sign explicit go-live authorization

### Optional Automation (Claude Code — if requested)
- [ ] Cron for daily executive report (7 AM)
- [ ] Cron for background learning full discovery (nightly)
- [ ] Outlook discovery automation (currently manual only)
- [ ] Background learning `extract_and_classify()` batch job

---

## Post Gate 5 — Go-Live Authorization Required

These items require Buck's explicit go-live approval before proceeding:

- [ ] Flip connector registry entries to write mode (per source, per project, explicitly approved)
- [ ] Enable direct HubSpot write-back for approved approval queue items
- [ ] Enable Google Drive live folder writes (off test mode)
- [ ] Enable Houzz live updates (off draft mode)

---

## Future Phases (No Timeline Set)

### Phase 7 — Agents
- [ ] Project Brain agent (autonomous intelligence synthesis)
- [ ] Bid leveling agent enhancement (auto-award recommendation + HubSpot attachment sync after /mcp auth)
- [ ] RFI agent (auto-draft + routing)
- [ ] Schedule agent (variance monitoring + alerts)

### Phase 8 — Dashboard
- [ ] Live operations dashboard (MVP ops + approval queue + BL pipeline)
- [ ] ROI dashboard (cumulative savings visualization)
- [ ] Executive briefing dashboard (auto-generated AM briefing)
- [ ] Mobile-friendly interface

---

## Known Issues / Gaps

| Priority | Item | Status |
|----------|------|--------|
| MEDIUM | WF-001/002/005/006 don't log workflow_events | Deferred to Phase 7 |
| MEDIUM | vendor_memory + drive_memory Qdrant empty | Re-run embed pipeline |
| LOW | No Outlook automated discovery | Manual `discover()` only |
| LOW | No launchd for WF-PM daily / exec health report | Phase 7 |

---

## Validated and Live (do not rebuild)

All of the following are built, tested, and active:
- Platform Integration Layer (39/39 tests) — Phase 15
- MVP Sprint 1 Daily Operations (48/48 tests) — Phase 16
- SOP Execution Layer (Phases 14a–14i)
- Workflow Engine (18 workflows)
- Intelligence Services (9 services)
- Infrastructure (Postgres, Redis, MinIO, Qdrant, launchd)
