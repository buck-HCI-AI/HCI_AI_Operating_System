# HCI Business Process Backlog
*Source: HCI-OR-001 Platform Opportunity Report | Ingested: 2026-06-27*
*Status: ROADMAP — Do not implement without Chief Architect review*

---

## Phase 1 — Quick Wins (0-30 days) | HIGH value, LOW/MEDIUM complexity

Sorted by priority score (descending)

| ID | Name | Recommendation | Score | BV | FI | PM | EX | TC | Owner |
|----|------|---------------|-------|----|----|----|----|----|----|
| HP-18 | Tasks & Punchlist | EXTEND | 18.0 | 5 | 5 | 4 | 4 | 1 | SS + PM |
| HP-06 | Change Orders (AI drafting) | EXTEND | 18.0 | 5 | 3 | 5 | 5 | 1 | PM |
| HP-13 | Selection Boards | EXTEND | 17.0 | 5 | 3 | 5 | 4 | 1 | PM + Client |
| HS-02 | Companies / COI Engine | INTEGRATE+EXTEND | 17.0 | 5 | 3 | 4 | 5 | 1 | PM |
| HS-01 | Contacts / COI tracking | INTEGRATE+EXTEND | 16.0 | 5 | 3 | 4 | 4 | 1 | PM |
| HS-18 | Dashboards & Reports | EXTEND | 16.0 | 5 | 2 | 4 | 5 | 1 | Buck |
| HS-12 | Forms (COI submission) | EXTEND | 15.0 | 5 | 2 | 4 | 4 | 1 | PM |
| HS-15 | Documents (bid tracking) | EXTEND | 15.0 | 5 | 2 | 4 | 4 | 1 | PM |
| HS-13 | Lists / Bid Segments | EXTEND | 14.0 | 4 | 2 | 4 | 4 | 1 | PM |
| HP-16 | Files & Photos | EXTEND | 13.0 | 3 | 4 | 3 | 3 | 1 | SS |
| HS-04 | Tasks (auto-create) | EXTEND | 12.0 | 3 | 2 | 4 | 3 | 1 | PM |
| HS-07 | Meetings embed | INTEGRATE | 11.0 | 3 | 2 | 3 | 3 | 1 | PM |
| HS-11 | Workflows (upgrade) | UPGRADE+INTEGRATE | 9.0 | 5 | 3 | 5 | 5 | 2 | Buck (decision: $70/mo) |
| HP-01 | Projects (bridge) | INTEGRATE | 6.3 | 5 | 4 | 5 | 5 | 3 | PM + n8n |
| HP-17 | Schedule (AI gen) | EXTEND | 6.7 | 5 | 5 | 5 | 5 | 3 | SS + PM |
| HP-09 | Budget (activate) | EXTEND | 6.0 | 5 | 3 | 5 | 5 | 3 | PM |
| HS-19 | HubSpot↔Houzz bridge | EXTEND | 5.7 | 5 | 3 | 4 | 5 | 3 | n8n |

**Phase 1 Decision Required from Buck:**
- HS-11: HubSpot Workflows upgrade ($70/mo) — COI tracking + bid follow-up alone pay for it in 1 week

---

## Phase 2 — Core Buildout (30-90 days) | HIGH/MEDIUM value, MEDIUM complexity

| ID | Name | Recommendation | Score | BV | FI | PM | EX | TC |
|----|------|---------------|-------|----|----|----|----|-----|
| HS-03 | Deals Pipeline (bridge) | INTEGRATE+EXTEND | 6.0 | 5 | 3 | 5 | 5 | 3 |
| HS-17 | Activities AI Summary | INTEGRATE | 5.3 | 5 | 2 | 4 | 5 | 3 |
| HS-20 | Webhooks (real-time) | EXTEND | 5.3 | 5 | 2 | 4 | 5 | 3 |
| HS-09 | Quotes / ROM generation | EXTEND | 5.3 | 5 | 1 | 5 | 5 | 3 |
| HP-03 | Contracts (activate) | EXTEND | 5.3 | 5 | 1 | 5 | 5 | 3 |
| HP-04 | Estimates (activate) | EXTEND | 5.7 | 5 | 2 | 5 | 5 | 3 |
| HP-05 | Invoices (milestone) | EXTEND | 5.0 | 5 | 1 | 4 | 5 | 3 |
| HP-14 | Selections Tracker | INTEGRATE | 5.0 | 4 | 3 | 4 | 4 | 3 |
| HS-05 | Notes AI indexing | EXTEND | 4.0 | 3 | 2 | 4 | 3 | 3 |
| HS-06 | Emails / Sequences | EXTEND | 5.0 | 5 | 2 | 4 | 4 | 3 |
| HP-02 | Leads (303 homeowners) | INTEGRATE | 4.7 | 5 | 1 | 3 | 5 | 3 |
| HP-07 | Purchase Orders | EXTEND | 4.3 | 3 | 2 | 4 | 4 | 3 |
| HS-10 | Products catalog | EXTEND | 10.0 | 3 | 1 | 3 | 3 | 1 |
| HS-14 | Marketing Emails | EXTEND | 10.0 | 3 | 1 | 3 | 3 | 1 |
| HS-16 | Attachments | EXTEND | 11.0 | 3 | 2 | 3 | 3 | 1 |

---

## Phase 3 — Advanced (90-180 days)

| ID | Name | Recommendation | Score | Notes |
|----|------|---------------|-------|-------|
| HS-08 | Line Items / CPQ | EXTEND (future) | 2.4 | Requires HS-09 + HS-10 complete |
| HP-08 | Retainers | EXTEND (future) | 11.0 | Standard practice — activate post contract flow |

---

## Phase 4 — Evaluate / Ignore (180+ days)

| ID | Name | Recommendation | Score | Reason |
|----|------|---------------|-------|--------|
| HP-10 | Takeoffs | EVALUATE | 2.2 | AI takeoff technology emerging — revisit 2027 |
| HP-15 | Houzz Bids | EVALUATE | 2.2 | Sub-vendor adoption risk — evaluate post pilot |
| HP-11 | 3D Floor Plans | IGNORE | 1.3 | Below Aspen luxury market quality bar |
| HP-12 | Mood Boards | IGNORE | 4.0 | GC, not design-build — not applicable |

---

## Prerequisite Decision Queue

| Decision | Owner | Impact | Unlocks |
|----------|-------|--------|---------|
| HubSpot Workflows upgrade ($70/mo) | Buck | Unlocks 7 Phase 1 automations | HS-11, HS-06 Sequences, HS-20 |
| Houzz Pro Browser extraction (15 min × 3 projects) | Buck | Unlocks Phases 1-2 Houzz automations | HP-09, HP-17, HP-04, BTW-7 |
| HubSpot → Houzz Project bridge build | n8n/PM | Closes most critical integration gap | HP-01, HS-19, HS-03 |
