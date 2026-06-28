---
source_agent: Claude Code
destination_agent: Browser Claude
document_type: chief_architect_directive
priority: high
status: pending
related_system: Houzz Pro
title: Houzz Data Extraction — Gate 5 Pilot Projects
created_at: 2026-06-28
summary: Extract schedule, tasks, POs, and budget data for 64 Eastwood, 101 Francis, and 1355 Riverside from Houzz Pro. Required to unblock WF-009 Schedule Intelligence and BTW-7 Field Enhancements.
---

# Houzz Data Extraction Directive — Gate 5 Pilot

## Why This Matters
The HCI AI OS has 0 records in these critical tables:
- `houzz_schedule_items` — 0 records (needed for schedule intelligence)
- `houzz_tasks` — 0 records (needed for superintendent console)
- `houzz_purchase_orders` — 0 records (needed for delivery tracking)

WF-009 (Schedule Intelligence) and BTW-7 (Field Enhancements) are blocked until you extract this data.

---

## Your Session — 3 Projects, ~15 min each

### START HERE
1. Open Houzz Pro: https://pro.houzz.com
2. Sign in as Buck Adams (buck@hendricksoninc.com)
3. Navigate to **Projects**

---

## Project 1: 64 Eastwood

**For each tab below, extract ALL visible records and record them in your handoff file.**

### Schedule Tab
For each schedule item record:
- Title
- Start date
- End date
- Status (not started / in progress / complete)
- Assignee (if shown)
- % Complete (if shown)
- Parent item (if it's a subtask)

### Tasks Tab
For each task record:
- Title
- Description
- Status
- Priority
- Assigned to
- Due date
- Is punch list item? (yes/no)
- Location/room (if shown)

### Purchase Orders Tab
For each PO record:
- PO number
- Vendor name
- Description
- Status
- Amount
- Issue date
- Expected delivery date
- Received date (if applicable)

### Budget Tab
For each budget line:
- Category name
- Budgeted amount
- Committed amount
- Actual/spent amount

---

## Project 2: 101 Francis
Repeat exactly the same extraction: Schedule, Tasks, POs, Budget.

---

## Project 3: 1355 Riverside
Repeat exactly the same extraction: Schedule, Tasks, POs, Budget.

---

## How to Submit Your Findings

**Option A (Preferred — zero-click intake):**
Write your handoff file directly to:
```
/Users/buckadams/HCI_AI_Operating_System/Architecture/Agent_Handoff/Inbox/
```
Use the filename: `BROWSER_HANDOFF_HOUZZ_2026-06-28_EXTRACTION.md`

**Option B (Fallback):**
Save to Downloads — double-click `HCI_Process_Handoffs.command` on the Desktop.

---

## Handoff File Format

```markdown
---
source_agent: Browser Claude
destination_agent: Claude Code
document_type: houzz_export
priority: high
status: complete
related_system: Houzz Pro
title: Houzz Extraction — 64EW + 101F + 1355R Gate 5 Data
created_at: 2026-06-28
summary: Schedule, tasks, POs, and budget extracted for all 3 Gate 5 pilot projects
---

## 64 Eastwood — Schedule Items
| Title | Start | End | Status | Assignee | % |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## 64 Eastwood — Tasks
| Title | Status | Priority | Assigned To | Due Date | Punch List |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## 64 Eastwood — Purchase Orders
| PO # | Vendor | Description | Status | Amount | Issue Date | Expected |
|---|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

## 64 Eastwood — Budget
| Category | Budgeted | Committed | Actual |
|---|---|---|---|
| ... | ... | ... | ... |

[Repeat for 101 Francis and 1355 Riverside]
```

---

## What Claude Code Does Next
After you submit:
1. Validates the file through the Handoff Bus
2. Parses all records and inserts into the DB via `POST /api/v1/services/houzz/ingest`
3. Confirms record counts in each table
4. Activates WF-009 Schedule Intelligence
5. Sends you a ntfy confirmation

**~30 min total for 3 projects. This is the last manual step before full Schedule Intelligence goes live.**
