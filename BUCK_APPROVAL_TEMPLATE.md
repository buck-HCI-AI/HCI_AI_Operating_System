# Buck Approval Template
## HCI AI Operating System — Decision Record

**Purpose:** Standard format for items requiring Buck's approval.  
Items appear in the daily command center report. Buck replies yes/no/defer.

---

## How Approvals Work

1. An agent queues an approval item (via `approval_queue` DB table)
2. The command center report surfaces items in the **Decisions Needed** section
3. Buck reads the report and acts:
   - **Yes** → agent proceeds
   - **No** → agent abandons the item
   - **Defer** → item stays in queue for next report
   - **Modify** → agent revises and re-queues

Buck does NOT need to respond in conversation. He can email, text, or verbally say yes — Claude Code records it.

---

## Approval Categories

| Category | Gate | Examples | Who Implements |
|---|---|---|---|
| HubSpot write | Gate H | Update deal stage, contact fields | Claude Code |
| Client communication | Gate E | Email to client, text | Claude Code |
| Financial action | Gate F | Award bid, approve invoice | Buck directly |
| Code to main | Gate G | PR merge to GitHub main | Browser Claude |
| Vendor merge | Registry | Merge duplicate vendor records | Claude Code |
| Mining write | Mining gate | Create vendor record, update project | Claude Code |

---

## Approval Item Format

When an agent surfaces an item to Buck, it should be formatted as:

```
**Item [#]:** [What exactly will happen — be specific]

**Project:** [64EW / 101F / 1355R / HCI Admin]
**Impact:** [What changes if approved]
**Risk if deferred:** [What happens if Buck waits]
**Recommendation:** [Agent recommendation — Approve / Reject / Modify]

**Buck's response:** [ ] Approve  [ ] Reject  [ ] Defer  [ ] Modify: ___________
```

---

## Example

```
**Item 3:** Merge "Ajax Mechanical Services" (7 duplicate entries in vendor registry)
into a single record with the most complete data from the 7 entries.

**Project:** HCI Admin — Vendor Registry
**Impact:** 7 rows become 1; all bid entries remain linked via normalized ID
**Risk if deferred:** Duplicate vendors inflate bid count and muddy reporting
**Recommendation:** Approve — clear duplicate, zero data loss

**Buck's response:** [x] Approve  [ ] Reject  [ ] Defer  [ ] Modify: ___________
```

---

## Batch Approvals

For large batches (>5 items of the same type), Claude Code will group them:

```
**Batch Approval — Vendor Registry Merges (6 groups)**

Group A: Ajax Mechanical Services (7 → 1)
Group B: 2H Mechanical (2 → 1)  
Group C: AAA Mountain Waterproofing (2 → 1)
Group D: ANB Bank (2 → 1)
Group E: Ajac Stone (2 → 1)
Group F: Ajax Electric (2 → 1)

**Buck's response:**
[ ] Approve ALL 6 groups
[ ] Approve specific: _____________
[ ] Reject ALL
[ ] Defer
```

---

*Approval Template | HCI AI Operating System | Hendrickson Construction, Inc.*
