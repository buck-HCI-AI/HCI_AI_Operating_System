# BOOK_01 — Volume 12: Decision Intelligence

**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_Business_Operating_Layer_BOOK01_Decision_KPI_Master_Directive_v1.0

---

## Why HCI Captures Decisions

In construction, you make the same decisions on every project: What to include in scope. Which subcontractor to award. How to respond to an unexpected site condition. Whether to accept a client's change request.

Without a system, the same decision is re-made from scratch each time — sometimes well, sometimes poorly — and the reasoning disappears when the project closes.

With Decision Intelligence, every significant decision becomes knowledge. The reasoning, context, alternatives considered, risk accepted, and outcome are recorded and searchable. The next project starts smarter.

---

## What Qualifies as a Decision Record

Not every daily choice needs a formal decision record. Decision records are created for:

| Type | Examples |
|------|---------|
| Award | Choosing a subcontractor for a specific scope |
| Scope | Including or excluding a significant scope item |
| Risk | Accepting a contract term, site condition, or cost risk |
| Change | Approving, rejecting, or negotiating a client change order |
| Schedule | Accelerating, crashing, or accepting a delay to the schedule |
| Procurement | Substituting a specified material or system |
| Team | Assigning PM, Superintendent, or key personnel to a project |
| Design | Selecting a design option, system, or specification |
| Legal | Deciding whether to dispute, accept, or escalate a contract issue |
| Lessons | Deciding to change a standard practice based on project experience |

---

## Decision Record Structure

Every decision record contains:

| Field | Description |
|-------|-------------|
| `decision_id` | Unique ID |
| `project_id` | Project this decision belongs to (null for company-level) |
| `decision_type` | Award / Scope / Risk / Change / Schedule / Procurement / Team / Design / Legal / Lessons |
| `decision_date` | When the decision was made |
| `decision_maker` | Who made the decision |
| `approver` | Who had authority to approve (may be same as decision_maker) |
| `context` | Situation that required a decision |
| `options_considered` | What alternatives were evaluated |
| `selected_option` | What was decided |
| `rationale` | Why this option was chosen over others |
| `risk_accepted` | Known risks or downsides of this choice |
| `cost_impact` | Estimated cost impact (positive or negative) |
| `schedule_impact` | Estimated schedule impact |
| `related_documents` | RFI, CO, bid, contract — linked by document ID |
| `outcome` | Filled in at closeout — did the decision work out? |
| `lessons_learned` | Indexed for future projects |

---

## How Decisions Are Captured

**In meeting notes:** AI extracts decision language from WF-002 meeting notes. PM confirms and records.

**At approval gates:** Every SOP approval gate that moves a deliverable to "Approved" status creates a decision record.

**At bid leveling:** The award recommendation and Buck's award decision create a decision record with all options compared.

**At change order approval:** Every CO approval or rejection creates a decision record.

**Post-project:** The post-project review (SOP 42) surface decisions that were made during the project and identifies which were good and which should be made differently.

---

## Searching the Decision Library

The decision library is indexed and searchable:

- "What subcontractors have we used for structural steel in the last 5 years?"
- "How have we handled discovery of underground utilities on past projects?"
- "What bid leveling decisions were made on projects with more than 3 bidders?"
- "Show me all decisions that were reversed during construction."

Decision intelligence answers these questions from the record — not from the memory of whoever happens to be in the room.

---

## Decision Intelligence Service

Service path: `03_Source_Code/services/decision_intelligence/`

The service handles:
- `POST /api/v1/decisions/` — create a decision record
- `GET /api/v1/decisions/{project_id}` — get all decisions for a project
- `GET /api/v1/decisions/search?q={query}` — semantic search across all decisions
- `PATCH /api/v1/decisions/{id}/outcome` — update outcome at closeout
- Dashboard: decision count by type, approval status, outcome rating

---

## Decision KPIs

| KPI | Target |
|-----|--------|
| Decisions with rationale documented | 100% of award and risk decisions |
| Decision records updated with outcome | 100% by project closeout |
| Time from decision to record creation | < 24 hours |
| Decision search used pre-award | Tracked per project |

---

*Standard: `docs/DECISION_INTELLIGENCE_STANDARD.md`*  
*Related: SOP 36 (Decision Log), Volume 13 (KPI Intelligence), Volume 15 (Business Process Library)*
