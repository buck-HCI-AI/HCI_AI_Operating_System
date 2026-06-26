# BOOK_01 — Volume 11: Closeout and Warranty

**Version:** 1.0 | **Date:** 2026-06-25

---

## Why Closeout Is a System Phase, Not a Final Task

Project closeout is not a sprint at the end of a job. It is a continuous process that runs in parallel with field execution from substantial completion through final acceptance and warranty period.

Projects that "sprint to closeout" produce:
- Incomplete punch lists
- Missing closeout documents
- Unresolved warranty items
- Uncollected final waivers
- Strained client relationships at the moment of final invoice

HCI AI tracks closeout items from the moment they are identified — not from when someone panics two weeks before the final inspection.

---

## Closeout Sequence (SOP 39-42)

```
Substantial Completion Inspection
  → Punch List Created (SOP 39) — every item logged, assigned, due date set
    → Punch List Execution — items completed and confirmed by Super
      → Owner Manual and Closeout Documents Assembled (SOP 40)
        → Final Inspection
          → Certificate of Substantial Completion
            → Warranty Period Begins (SOP 41)
              → Post-Project Review (SOP 42)
                → Lessons Learned Indexed — Project Archived
```

---

## Punch List (SOP 39)

Punch list items are tracked from creation to closure:

| Field | Description |
|-------|-------------|
| Item Number | Sequential per project |
| Description | Specific: scope, location, defect |
| Assigned To | Trade contractor responsible |
| Status | Open → In Progress → Complete → Verified |
| Due Date | Target completion date |
| Verified By | Who confirmed completion (PM or Super) |
| Photos | Before/after documentation |

**AI role in punch list:**
- AI reviews final inspection notes and daily logs to identify items
- Generates structured punch list from inspection records
- Tracks open item count and days since creation
- PM reviews and confirms before distributing to subs

**No final invoice without all punch items either closed or formally accepted by owner.**

---

## Owner Manual and Closeout Documents (SOP 40)

Every project produces a closeout package:

| Document | Required |
|---------|---------|
| As-Built Drawings | Yes |
| Product Data and Warranties (by sub) | Yes |
| O&M Manuals | Yes |
| Attic Stock | If required by contract |
| Testing and Commissioning Reports | If applicable |
| Training Records (owner's staff) | If applicable |
| Inspection Certificates (occupancy, life safety) | Yes |
| Final Lien Waivers (all trades) | Yes |
| Final W-9s | If not already on file |

AI tracks which closeout documents are on file and which are outstanding. PM is notified of outstanding items weekly during the closeout phase.

---

## Warranty (SOP 41)

Warranty tracking begins at substantial completion:
- Warranty start date and end date per trade
- Warranty contact (sub PM, phone, email)
- Claim log: date received, description, scope, sub notified, resolution

**Warranty claims are logged within 24 hours of receipt.** Sub is notified same day with required response date.

**Warranty response SLA:** Sub must acknowledge within 48 hours. Resolution timeline established at acknowledgment. Sub failure to respond triggers PM escalation and Buck notification.

---

## Post-Project Review (SOP 42)

Every project closes with a structured post-project review. It is not optional.

Review questions:
1. What did we bid vs. what we actually spent? (By scope line)
2. What went right that we should repeat on the next project?
3. What went wrong that we must fix on the next project?
4. Were there scope gaps in our bid package?
5. How did each subcontractor perform?
6. Was the client satisfied? Would they hire HCI again?
7. What would we bid differently?

**AI role:** AI compiles the project record (budget vs. actual, schedule variance, change order history, RFI volume, punch list count) and drafts the review form. PM and Buck complete the qualitative sections.

**Output:** Post-project review is stored and indexed in the lessons-learned service. Every future project can query: "What did we learn on projects like this?"

---

## Closeout KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Punch items resolved within 30 days of SC | > 90% | Punch list log |
| Closeout package delivered within 45 days of SC | 100% | Closeout tracker |
| Final lien waivers collected | 100% | Waiver log |
| Warranty claims responded to within 48 hours | 100% | Warranty log |
| Post-project review completed within 60 days of Final | 100% | Review log |

---

*Related SOPs: SOP 39 (Punch List), SOP 40 (Owner Manual / Closeout), SOP 41 (Warranty), SOP 42 (Post-Project Review)*  
*Lessons-learned service: `03_Source_Code/services/lessons_learned/`*
