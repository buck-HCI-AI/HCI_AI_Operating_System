# AI Opportunity Matrix
*HCI AI Operating System | Source: HCI-OR-001 | 2026-06-27*
*North Star: "Does this help someone build a better project?"*

---

## AI Opportunities by Category

### Category A: AI Drafting & Generation

| ID | Opportunity | Trigger | AI Action | Human Gate | Impact |
|----|------------|---------|-----------|------------|--------|
| AI-01 | COI Renewal Emails | COI expires < 30 days | Draft renewal email for company | PM reviews → send | 4 hrs/week saved |
| AI-02 | Bid Invitation Emails | Deal stage = "Sent Out" | Draft invitation per CSI division | PM reviews → send | 3 hrs/week saved |
| AI-03 | Change Order Drafts | Daily log: out-of-scope keywords | Generate formal CO language | PM reviews → submit | Risk reduction |
| AI-04 | Punchlist Generation | Project = Closeout | Scan 30 days of daily logs → punchlist | SS reviews → assign | 4 hrs/project saved |
| AI-05 | Selection Reminders | Selection overdue 7 days | Draft client follow-up message | PM reviews → send | Schedule risk reduced |
| AI-06 | Pre-meeting Briefs | Meeting scheduled | Summarize deal history, last contact, open items | Auto-delivered | Meeting quality |
| AI-07 | Lead Response | Houzz lead arrives | Draft personalized response from homeowner profile | Buck reviews → send | 302 leads waiting |
| AI-08 | ROM Generation | Deal = "ROM Submitted" stage | Generate ROM from deal scope + historical data | PM reviews → send | Bid process consistency |

---

### Category B: AI Analysis & Scoring

| ID | Opportunity | Data Source | AI Analysis | Output | Impact |
|----|------------|-------------|-------------|--------|--------|
| AI-09 | Sub Performance Scoring | HubSpot engagements + notes | Score: responsiveness, pricing, relationship | Sub health score in HCI AI OS | Better bid list |
| AI-10 | Deal Summarization | HubSpot activities (2,135 engagements) | Summarize deal history, key decisions | Per-deal intelligence card | PM efficiency |
| AI-11 | Budget Variance Alert | Houzz Budget (future) | Detect line items >10% over budget | ntfy → PM | Profitability |
| AI-12 | Schedule Delay Detection | Houzz Schedule (future) | Identify critical path delays | ntfy → PM + SS | Delivery risk |
| AI-13 | Selections Bottleneck Report | Houzz Selections Tracker XLS | Parse weekly export → identify stalled selections | Weekly PM report | Material delays |
| AI-14 | Lead Scoring | Houzz Leads (303 homeowners) | Score by project size, location, timeline | Prioritized lead list | Revenue pipeline |
| AI-15 | Estimate Generation | Project scope + historical costs | AI estimate with unit costs | PM reviews → submits | Bid accuracy |

---

### Category C: AI Detection & Alerts

| ID | Opportunity | Trigger | AI Detection | Alert | Impact |
|----|------------|---------|--------------|-------|--------|
| AI-16 | COI Gap Risk | Daily cron | Flag subs on active jobs with expired COI | ntfy (urgent) | Liability |
| AI-17 | Bid Package Staleness | Daily cron | Flag bid packages >14 days no response | ntfy → PM action | Procurement risk |
| AI-18 | Unsigned Change Order | Weekly | Flag COs outstanding >7 days | ntfy → PM | Revenue/dispute risk |
| AI-19 | Client Contact Gap | HubSpot engagements | Days since last client contact >7 days | PM workspace alert | Relationship health |
| AI-20 | Missing Documents | Milestone trigger | Flag projects missing contract, approved scope, signed CO | Executive dashboard | Risk management |

---

## AI Maturity Map

| AI Opportunity | Maturity Level | Currently Live | Phase to Activate |
|---------------|---------------|---------------|------------------|
| AI-17 Bid staleness | Level 3 (Intelligent) | ✅ YES — project_risks_computed | Active now |
| AI-16 COI gap | Level 3 (Intelligent) | Partial — no cron today | Phase 1 |
| AI-19 Client contact gap | Level 3 (Intelligent) | ✅ YES — BTW-8 PM workspace | Active now |
| AI-10 Deal summarization | Level 3 (Intelligent) | ✅ YES — hubspot_activities | Active now |
| AI-01 COI renewal emails | Level 5 (Autonomous) | NO — needs n8n COI workflow | Phase 1 |
| AI-03 CO drafting | Level 5 (Autonomous) | NO — Houzz CO unused | Phase 2 |
| AI-04 Punchlist generation | Level 5 (Autonomous) | NO — needs daily log parsing | Phase 2 |
| AI-11 Budget variance | Level 4 (Predictive) | NO — Houzz Budget unused | Phase 2 |
| AI-12 Schedule delay | Level 4 (Predictive) | NO — Houzz Schedule unused | Phase 2 |
| AI-15 Estimate generation | Level 4 (Predictive) | NO — needs historical cost data | Phase 3 |
| AI-14 Lead scoring | Level 4 (Predictive) | NO — Houzz Leads not synced | Phase 2 |

---

## Highest ROI AI Opportunities (unbuilt, ranked)

1. **AI-01 — COI Renewal Emails** — 4 hrs/week saved, zero liability risk, n8n cron + Claude Haiku, Phase 1
2. **AI-03 — Change Order Drafting** — Revenue protection, dispute reduction, low complexity once Houzz CO activated
3. **AI-04 — Punchlist Generation** — 4 hrs/project saved, closeout quality improvement
4. **AI-07 — Lead Response** — 302+ homeowners waiting → immediate revenue pipeline
5. **AI-13 — Selections Bottleneck** — Cascade prevention on luxury projects where selections block trades

---

## Cross-Reference: AI OS Current vs. Needed

| HCI AI OS Component | Uses AI Today | Missing AI Input |
|--------------------|--------------|-----------------|
| Project Brain | ✅ Risk detection, summaries | Houzz budget, schedule, CO data |
| Predictive Engine | ✅ 7 prediction types | Houzz schedule (confidence low without it) |
| Executive Morning Brief | ✅ Daily summary | Houzz financial data |
| PM Workspace | ✅ BTW-8 ranked actions | CO status, selection alerts |
| SS Console | ✅ Today's priorities | Punchlist AI, photo tagging |
| Knowledge Graph | ❌ Not built (BTW-9) | All of the above |
