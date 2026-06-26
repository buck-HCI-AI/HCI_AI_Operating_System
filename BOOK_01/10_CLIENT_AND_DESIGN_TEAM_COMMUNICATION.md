# BOOK_01 — Volume 10: Client and Design Team Communication

**Version:** 1.0 | **Date:** 2026-06-25

---

## Communication Principle

All communication with clients and the design team must be:
- **Timely:** The right information at the right time
- **Accurate:** Based on the project record — not memory or email
- **Traceable:** Logged so that what was said is retrievable
- **Authorized:** Client-facing communication reviewed before it goes out

AI drafts communication. Humans review and send.

---

## Client Communication Model

| Communication Type | Frequency | Drafter | Reviewer | Authority |
|-------------------|-----------|---------|---------|-----------|
| Weekly Status Report | Weekly (Friday) | AI | PM | Buck signs off |
| Monthly Owner Report | Monthly | AI | PM + Buck | Buck sends |
| RFI Responses | As needed | Design team | PM | PM logs |
| Change Order Submission | As needed | AI draft | PM | Buck approves |
| Meeting Notes | After each meeting | AI (WF-002) | PM | PM sends |
| Milestone Notification | Per contract | PM | Buck | PM sends |
| Delay Notification | Per contract (if required) | AI draft | PM + Buck | Buck sends |
| Claim or Dispute | As needed | PM + Attorney | Buck | Buck sends |

---

## Weekly Status Report

The weekly status report is the primary client communication. It must be:
- Consistent in format every week
- Based on data — not assembled from email
- Reviewed and signed off by Buck before delivery

**AI generates the weekly report from:**
- Daily logs (work accomplished)
- Schedule comparison (planned vs. actual)
- Budget summary (current contract value, approved changes, percent complete)
- Open items: RFIs, submittals, change orders pending
- Issues and risks
- Next week priorities

**PM reviews:** Edits narrative, confirms accuracy, adds context.
**Buck reviews:** Signs off before send.
**Delivery:** Every Friday by 5 PM.

---

## Meeting Notes (WF-002 — Meeting Intelligence)

Every owner, design team, or coordination meeting produces meeting notes through WF-002:

1. Meeting occurs (recorded or notes taken in real time)
2. PM submits meeting notes via WF-002 endpoint
3. AI formats, extracts action items with owners and due dates, identifies decisions made
4. PM reviews output
5. PM sends to meeting attendees within 24 hours

**Decision log:** Every decision recorded in a meeting note is automatically added to the project decision log (SOP 36 / Decision Intelligence service).

---

## Design Team Communication

All design team communication is logged:
- RFIs (formal — see Volume 09)
- ASIs (Architect's Supplemental Instructions — received, logged, scope impact assessed)
- Drawing revisions (logged, prior version archived, project brain updated)
- Addenda (received, logged, distributed to subs, acknowledged)

**No verbal design change is acted upon without written confirmation.** If the architect says it verbally, PM follows up in writing the same day. If written confirmation is not received in 5 days, PM reconfirms.

---

## Communication Authorization

AI may NOT send client-facing communication autonomously. This is a hard system rule.

| Action | Who Can Authorize |
|--------|------------------|
| Send weekly status report | Buck (review + approval) |
| Send change order to owner | Buck (approval required) |
| Send meeting notes | PM (review required) |
| Send delay notification | Buck |
| Send claim notice | Buck + Attorney |
| Send any client email | PM (at minimum) |

---

## Client Communication KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Weekly report delivered by Friday 5 PM | 100% | Report log |
| Meeting notes sent within 24 hours | > 90% | WF-002 timestamp |
| Client RFI and CO communications acknowledged | 100% | Communication log |
| Verbal design direction confirmed in writing | 100% | Communication log |

---

*Related: WF-002 Meeting Intelligence | SOP 34 (Client Communication) | SOP 35 (Meeting Notes) | SOP 36 (Decision Log) | SOP 37 (Weekly Update)*  
*Meeting notes workflow: `03_Source_Code/api/routers/wf_002.py`*
