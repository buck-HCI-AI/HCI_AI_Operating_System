# Executive Inbox
## HCI AI Operating System — Owner Decisions Only

**Last Updated:** 2026-06-27  
**Authority:** Chief Architect Directive — Phase II (Objective 3)  
**Format:** Decision / Recommendation / Confidence / Business Impact / Risk / Deadline

---

> **Instructions:** Review each item below. Mark your response. Claude Code executes approved items in the next session.
> No raw logs. No code. No implementation details. Owner decisions only.

---

## 🔴 Active Decisions — Review Now

---

### EXEC-001 — Vendor Registry Merges
**Decision:** Merge 17 duplicate vendor records (6 groups) into 6 clean records. All bid entries remain linked.

**Recommendation:** Approve ALL  
**Confidence:** High — mechanical dedup, zero data loss, all bid associations preserved  
**Business Impact:** Vendor count 392 → 386. Reporting becomes accurate. Duplicate vendor intelligence eliminated.  
**Risk:** Low. Additive merge with backup before execution. Reversible.  
**Deadline:** No hard deadline — but delays vendor intelligence accuracy

| Group | From | To |
|---|---|---|
| A | Ajax Mechanical Services × 7 | 1 record |
| B | 2H Mechanical × 2 | 1 record |
| C | AAA Mountain Waterproofing × 2 | 1 record |
| D | ANB Bank × 2 | 1 record |
| E | Ajac Stone × 2 | 1 record |
| F | Ajax Electric × 2 | 1 record |

**Buck's response:** [ ] Approve ALL  [ ] Approve specific: ___  [ ] Defer  [ ] Reject

---

### EXEC-002 — Write 101 Francis to Houzz Database
**Decision:** Persist 101 Francis project record to `houzz_projects` table using real Houzz ID `3218059`.

**Recommendation:** Approve  
**Confidence:** High — project ID confirmed, data validated by Browser Claude  
**Business Impact:** Unlocks Houzz intelligence pipeline. HouzzMiner activates. Daily log + schedule intelligence begins for 101 Francis.  
**Risk:** Low. Internal database write only. Idempotent — safe to re-run.  
**Deadline:** ASAP — Gate 5 closes 2026-07-01. Houzz intelligence needed before then.

**Buck's response:** [ ] Approve  [ ] Defer  [ ] Reject

---

### EXEC-003 — Import Pacific Concrete Bid ($185,000)
**Decision:** Import Pacific Concrete Inc. bid record into HCI database. Division: Concrete. Amount: $185,000. Project: 101 Francis.

**Recommendation:** Approve  
**Confidence:** High — bid data from procurement process, standard import  
**Business Impact:** Bid visible in HCI bid intelligence, eligible for leveling analysis.  
**Risk:** Low. Internal record only. No external notification.  
**Deadline:** Before next bid leveling run

**Buck's response:** [ ] Approve  [ ] Defer  [ ] Reject

---

### EXEC-004 — Upload 1355 Riverside Div 16 Bid Leveling to Drive
**Decision:** Upload bid leveling Excel file for 1355 Riverside Division 16 Electrical to Google Drive.

**Recommendation:** Approve  
**Confidence:** High — file already generated, standard Drive upload  
**Business Impact:** File accessible from Drive for team sharing. Leveling analysis preserved.  
**Risk:** Low. Drive upload only. No external communications triggered.  
**Deadline:** No hard deadline

**Buck's response:** [ ] Approve  [ ] Defer  [ ] Reject

---

### EXEC-005 — Commit 1355 Riverside Daily Log (2026-06-26)
**Decision:** Write daily log entry for 1355 Riverside dated June 26 to HCI database.

**Recommendation:** Approve  
**Confidence:** High — standard daily log record, already queued  
**Business Impact:** Log becomes part of project intelligence. Feeds HouzzMiner and lessons-learned analysis.  
**Risk:** Low. Internal record. Idempotent.  
**Deadline:** Log aging — approve soon for accuracy

**Buck's response:** [ ] Approve  [ ] Defer  [ ] Reject

---

## 🟡 Owner Holds — Action When Ready

---

### EXEC-D01 — GitHub Repo Privacy
**Decision:** Make the GitHub repository private. Currently public — any previously committed secrets are findable in git history.

**Recommendation:** Make private  
**Confidence:** High — no business reason to be public; reduces exposure risk  
**Business Impact:** Eliminates future credential exposure risk. ChatGPT/Browser Claude still work (via Drive/ngrok).  
**Risk:** Low. Existing collaborators keep access. GitHub raw URLs stop working publicly.  
**Deadline:** No hard deadline — but recommended before next production go-live

**Buck's response:** [ ] Make private (GitHub Settings → Danger Zone → Change visibility)  [ ] Keep public  [ ] Defer

---

### EXEC-D02 — HubSpot Connected Inbox
**Decision:** Connect Buck's personal email to HubSpot for email tracking.

**Recommendation:** Connect  
**Confidence:** Medium — depends on Buck's email preferences  
**Business Impact:** HubSpot tracks email interactions with clients/vendors automatically. Reduces manual CRM updates.  
**Risk:** Low. Email read-only tracking. Can be disconnected any time.  
**Deadline:** No hard deadline — Sprint 3 email digest feature benefits from this

**Buck's action required:** HubSpot Settings → Email → Connect personal email (Buck's UI action only — no agent can do this)

---

### EXEC-D03 — Branch Protection on GitHub main
**Decision:** Require pull request review before merging to `main` branch.

**Recommendation:** Enable  
**Confidence:** High — standard governance, prevents accidental direct pushes  
**Business Impact:** All changes go through PR review. Safer deployments.  
**Risk:** Low. Does not affect existing workflows.  
**Deadline:** Before Sprint 3 connector work begins

**Buck's action required:** GitHub → Settings → Branches → Add rule for `main` (Buck's UI action only)

---

### EXEC-D04 — 83 Sagebrusch HubSpot Deal
**Decision:** Confirm whether 83 Sagebrusch has an active HubSpot deal.

**Recommendation:** Check HubSpot and confirm  
**Confidence:** N/A — need Buck's confirmation  
**Business Impact:** Without deal ID, 83 Sagebrusch is not tracked in HCI project intelligence.  
**Risk:** Low  
**Deadline:** Before Gate 5 close (2026-07-01) if this project is in pilot scope

**Buck's action:** Confirm deal ID in HubSpot → tell Claude Code to add it to project registry

---

## ✅ Recently Resolved

| Item | Decision | Executed | By |
|---|---|---|---|
| Mining Engine go-live (ACR-004) | Approved | 2026-06-27 | Claude Code |
| Sprint 2 n8n workflows (9 workflows) | Approved | 2026-06-27 | Claude Code |
| API key rotation | Auto (security) | 2026-06-27 | Claude Code |
| Phase II roadmap documentation | Auto | 2026-06-27 | Claude Code |

---

## Approval Queue Summary

**Total pending:** 1,016 items  
**Surfaced here:** 5 active decisions (EXEC-001 through EXEC-005)  
**Remaining 1,011:** Vendor candidates and bid documents — handled by mining engine autonomously

The 986 vendor candidates do **not** require Buck's individual review. The Mining Engine uses them to build intelligence. They will be batched and surfaced here only when a merge or registry action is recommended.

---

*Executive Inbox | HCI AI Operating System | Hendrickson Construction, Inc.*  
*Phase II — Updated by: scripts/generate_command_center.py at 07:00 daily*  
*Format: APPROVAL_POLICY_REGISTRY.md (OWNER level only)*
