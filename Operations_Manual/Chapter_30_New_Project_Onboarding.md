# Chapter 30 — New Project Onboarding
*HCI AI Operations Manual — Part III: Governance*
**Author:** Claude Code (technical steps) + GBT (business process) | **Version:** 1.0 | **Date:** 2026-06-30

---

## 30.1 Overview

Every new project follows this onboarding sequence to enter the HCI AI OS. The system needs a project record before it can provide intelligence on it. Full onboarding takes approximately 30-60 minutes across all steps.

**Next project to onboard:** 246GW — 246 Gallo Way (monitored, pending full activation)

---

## 30.2 Onboarding Checklist

### Phase 1 — Business Setup (Buck + PM)

- [ ] **HubSpot deal created** — deal linked to client contact, scope defined, contract value entered
- [ ] **Project code assigned** — follow convention: {street number}{street abbreviation} (e.g., 246GW)
- [ ] **Contract value confirmed** — exact number for budget tracking
- [ ] **Superintendent assigned** — name and phone number
- [ ] **PM assigned** — who manages daily flow
- [ ] **Project start date confirmed** — for schedule baseline
- [ ] **Client contact(s) confirmed** — who receives client portal access

### Phase 2 — Drive Setup (Claude Code or PM)

- [ ] **Project folder created in Google Drive** — under HCI Projects master folder
- [ ] **Subfolders created:** Drawings, Specs, Contracts, Submittals, Photos, RFIs, SOWs
- [ ] **Drawings folder ID captured** — the Google Drive folder ID for `drawings_folder_id` in DB
- [ ] **Initial drawings uploaded** — structural, architectural, MEP as available

### Phase 3 — Database Record (Claude Code)

```sql
-- Insert project record
INSERT INTO projects (
    project_code, project_name, status, address,
    contract_value, hubspot_deal_id, drawings_folder_id,
    start_date
) VALUES (
    '246GW',
    '246 Gallo Way',
    'active',
    '246 Gallo Way, Aspen, CO',
    6300000.00,
    '321358358216',  -- HubSpot deal ID
    '{drive_folder_id}',
    '2026-07-01'
);
```

- [ ] Project record inserted with correct code, name, contract value, HubSpot deal ID
- [ ] Drawings folder ID populated (or flagged as pending)

### Phase 4 — Project Brain Initialization (Claude Code)

```bash
# Initialize project brain snapshot
curl -X POST "http://localhost:8000/api/v1/services/project-brain/{project_id}/initialize"

# Verify brain is live
curl -s "https://speculate-armband-retinal.ngrok-free.dev/gateway/project/246GW/brain"
```

- [ ] Initial health snapshot created (will be YELLOW until data populates)
- [ ] Risk detection running on new project

### Phase 5 — HubSpot Sync (Claude Code)

- [ ] Project linked to HubSpot deal in DB
- [ ] HubSpot sync run to pull contacts associated with deal
- [ ] Contacts appear in `contacts` table with project reference

### Phase 6 — Houzz Connection (Buck)

- [ ] Houzz project exists for this address
- [ ] Schedule imported (via browser extraction or direct API if available)
- [ ] Budget structure set up in Houzz
- [ ] SS added to Houzz project

### Phase 7 — n8n Workflow Activation (Claude Code)

- [ ] Project code added to AUTO-SS-MORNING workflow project list
- [ ] Project code added to AUTO-PM-WEEKLY workflow project list
- [ ] Project code added to AUTO-EVENT-HEALTH-CHECK project list
- [ ] Morning brief confirmed including new project

### Phase 8 — Notification Test (Claude Code)

```bash
# Test ntfy push for new project
curl -X POST "https://ntfy.sh/hci-ai-os-buck" \
  -H "Title: 246GW — Project Onboarding Complete" \
  -H "Priority: default" \
  -H "Tags: white_check_mark" \
  -d "246 Gallo Way is now live in HCI AI OS. Initial health: YELLOW (data populating). First morning brief tomorrow at 07:00."
```

- [ ] ntfy push received on Buck's phone
- [ ] Project appears in next morning brief

### Phase 9 — Bid Package Setup (PM)

- [ ] Bid tracker spreadsheet created in Google Sheets (copy from template)
- [ ] Sheet ID registered in system
- [ ] Initial bid packages entered (from project scope and drawings)
- [ ] First bid mining run: `POST /api/v1/services/mining/run-all`

### Phase 10 — Validation (Buck + Claude Code)

- [ ] `/gateway/project/246GW/brain` returns valid snapshot
- [ ] `/gateway/executive/report` includes 246GW
- [ ] Morning brief contains 246GW next morning
- [ ] ntfy push received for any risk detected

---

## 30.3 Time Estimates per Phase

| Phase | Time | Who |
|-------|------|-----|
| 1 — Business Setup | 30 min | Buck + PM |
| 2 — Drive Setup | 15 min | PM or Claude Code |
| 3 — DB Record | 5 min | Claude Code |
| 4 — Brain Init | 5 min | Claude Code |
| 5 — HubSpot Sync | 10 min | Claude Code (auto) |
| 6 — Houzz Connection | 30 min | Buck (browser extraction) |
| 7 — n8n Activation | 10 min | Claude Code |
| 8 — Notification Test | 5 min | Claude Code |
| 9 — Bid Package Setup | 30 min | PM |
| 10 — Validation | 10 min | Buck + Claude Code |

**Total: ~2.5 hours end-to-end (1.5 hours active, 1 hour wait)**

---

## 30.4 246GW — Next Steps

246GW is currently in the system as a monitored project. To move it to full production:

1. **Missing:** `drawings_folder_id` — Drive folder not yet created. PM to create and provide folder ID.
2. **Missing:** Superintendent name — needed to activate SS morning console for 246GW.
3. **Pending:** Houzz extraction — schedule data needed.
4. **Ready now:** DB record exists, brain initialized, HubSpot deal connected.

When Buck issues 246GW go-live authorization, Claude Code runs Phases 2+3+4+7+8 immediately.

---

## 30.5 Project Closure (End of Job)

When a project completes:

1. **Final walk-through and punch list closed in Houzz**
2. **Run lessons learned extraction:**
```bash
curl -X POST "http://localhost:8000/api/v1/services/mining/run" \
  -d '{"miner": "LessonsLearnedMiner", "project_code": "246GW", "dry_run": false}'
```
3. **Archive project:** `UPDATE projects SET status = 'completed' WHERE project_code = '246GW';`
4. **Qdrant archive:** final document embeddings preserved in `project_memory` collection
5. **Final executive report** sent to Buck
6. **Project Brain** snapshot marked final: `status = 'archived'`
7. **HubSpot deal** moved to Closed Won / Closed Lost

All data remains in system as learning material for future projects. Never delete project data.

---

*Cross-reference: Chapter 17 (Architecture), Chapter 22 (Database), Chapter 21 (Integrations)*
*See also: LIVE_PROJECT_STATE.md for current project roster*
