# Executive Inbox
## HCI AI Operating System — Owner Decisions Only

**Last Updated:** 2026-06-27  
**Authority:** Chief Architect Directive — Automation First (2026-06-27)  
**Rule:** Only items requiring Buck's decision appear here. Everything else is handled automatically.

---

> **How to use:**
> Scan the items below. Mark your decision next to each item.
> Claude Code reads this file and executes approved items in the next session.
> Deferred items stay until you act. Routine coordination never appears here.

---

## 🔴 Decisions Needed Now

### EXEC-001 — Vendor Registry Merges (6 groups, 17 records → 6)
**Category:** Registry cleanup  
**Action:** Approve batch merge of duplicate vendor records

| Group | Vendor Name | Duplicates → Merged |
|---|---|---|
| A | Ajax Mechanical Services | 7 → 1 |
| B | 2H Mechanical | 2 → 1 |
| C | AAA Mountain Waterproofing | 2 → 1 |
| D | ANB Bank | 2 → 1 |
| E | Ajac Stone | 2 → 1 |
| F | Ajax Electric | 2 → 1 |

**Impact:** Vendor count 392 → 386. All bid entries remain linked. Reporting cleaner.  
**Risk if deferred:** Duplicate vendors inflate bid reports and vendor intelligence.  
**Recommendation:** Approve ALL — zero data loss, all bid linkages preserved.

**Buck's decision:** [ ] Approve ALL  [ ] Approve specific groups: ___  [ ] Defer  [ ] Reject

---

### EXEC-002 — Approve 101 Francis Houzz Data Write
**Category:** Database write (internal)  
**Action:** Write 101 Francis project data queued by Browser Claude to houzz_projects

**Data:**
- houzz_project_id: `3218059`
- name: 101 Francis
- client: Adnan Rawjee
- address: 101 W Francis St, Aspen, CO 81611
- status: open

**Impact:** Enables HouzzMiner to process daily logs and schedule items once Browser Claude loads them.  
**Risk if deferred:** Houzz intelligence pipeline remains blocked.  
**Note:** This is an internal DB write, not an external commit.

**Buck's decision:** [ ] Approve  [ ] Defer  [ ] Reject

---

### EXEC-003 — Activate Bid Import (Pacific Concrete / $185K / 101 Francis)
**Category:** Bid import  
**Action:** Import bid record into HCI database  
**Details:** Pacific Concrete Inc, Concrete division, $185,000.00, 101 Francis  

**Buck's decision:** [ ] Approve import  [ ] Defer  [ ] Reject

---

### EXEC-004 — Upload Drive File (1355 Riverside Div 16 Bid Leveling)
**Category:** Google Drive write  
**Action:** Upload bid leveling Excel to Drive  

**Buck's decision:** [ ] Approve upload  [ ] Defer  [ ] Reject

---

### EXEC-005 — Daily Log Write (1355 Riverside 2026-06-26)
**Category:** Project documentation  
**Action:** Commit daily log entry for 1355 Riverside dated June 26  

**Buck's decision:** [ ] Approve  [ ] Defer  [ ] Reject

---

## 🟡 Deferred — Check When Ready

### EXEC-D01 — HubSpot Connected Inbox
**What:** Connect Buck's personal email to HubSpot  
**Where:** HubSpot Settings → Email → Connect personal email  
**Blocked by:** Requires Buck's UI action (can't be done by agents)  
**Impact:** Enables email tracking and HubSpot email integration

---

### EXEC-D02 — GitHub Branch Protection on main
**What:** Require PR review before merge to main  
**Where:** GitHub Settings → Branches → Add rule for `main`  
**Blocked by:** Requires Buck's GitHub UI action  
**Impact:** Prevents accidental direct pushes to main

---

### EXEC-D03 — GitHub Repo Privacy (Security Recommendation)
**What:** Make the GitHub repo private  
**Current state:** Public — any API keys committed in history are findable  
**Note:** Old key has been rotated, new key is not committed in plain text  
**Impact:** Eliminates future key exposure risk  
**Recommendation:** Recommend private — no business reason to be public

**Buck's decision:** [ ] Make private  [ ] Keep public  [ ] Defer

---

### EXEC-D04 — 83 Sagebrusch Project Setup
**What:** Confirm HubSpot deal ID for 83 Sagebrusch project  
**Current state:** Listed in project registry with no HubSpot deal ID  
**Action:** Buck confirms in HubSpot if deal exists

---

## ✅ Recently Approved

| Item | Approved | Executed |
|---|---|---|
| Mining Engine go-live (ACR-004) | 2026-06-27 | ✅ Claude Code |
| Sprint 2 n8n workflows (9 workflows) | 2026-06-27 | ✅ Claude Code |
| API key rotation | 2026-06-27 | ✅ Claude Code (auto — security) |

---

## 📊 Approval Queue Summary

**Total pending:** 1,016 items  
**By category:**

| Category | Count | Buck Action Needed |
|---|---|---|
| Vendor candidates (HubSpot sweep) | 986 | Optional batch review — agents auto-learn from queue |
| Bid documents discovered | 16 | Review → Approve/skip each bid |
| Bid correspondence | 8 | Review |
| DB writes | 2 | See EXEC-001 through EXEC-005 above |
| Houzz data | 1 | EXEC-002 above |
| Drive uploads | 1 | EXEC-004 above |

**Note:** The 986 vendor candidates are auto-learning items — Buck does not need to action all of them. The Mining Engine uses them to build vendor intelligence. However, Buck can approve specific ones to push them into the active vendor registry.

---

*Executive Inbox | HCI AI Operating System | Hendrickson Construction, Inc.*  
*Updated daily at 07:00 by scripts/generate_command_center.py*  
*All other coordination is handled automatically.*
