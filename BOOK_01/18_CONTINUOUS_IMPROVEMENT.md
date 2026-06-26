# BOOK_01 — Volume 18: Continuous Improvement

**Version:** 1.0 | **Date:** 2026-06-25

---

## How HCI Improves

The system improves through four feedback loops:

**Loop 1 — Post-Project Review (SOP 42)**  
After every project, the team reviews: what worked, what didn't, what we'd bid differently. This feeds the historical cost database, the lessons-learned index, and SOP updates.

**Loop 2 — KPI Trend Analysis**  
Over time, KPIs reveal patterns. If the bid margin on one trade category consistently erodes, that's a pricing problem or a scope problem. If daily logs are consistently submitted late on certain project types, that's a supervision rhythm problem. Trends surface opportunities.

**Loop 3 — SOP Audit**  
Every year (or after any significant project issue), SOPs are audited: Is the SOP current? Is the employee script accurate? Is the AI script producing the right output? Are the approval gates still at the right thresholds?

**Loop 4 — User Feedback**  
Buck, the PM, and the Superintendent use the system daily. Their friction points are tracked and fixed. If the daily log submission is cumbersome, simplify it. If the morning brief omits an important item, add it. Feedback is not a complaint — it is a system improvement request.

---

## The Learning Loop

Every project makes the system smarter:

```
Project Closes
  → Post-Project Review (SOP 42) → Lessons Learned indexed
  → Historical costs updated → Future budgets more accurate
  → Vendor performance logged → Future sub selection better informed
  → Decision outcomes noted → Future decision records more useful
  → KPI trends updated → Future thresholds better calibrated
  → SOP gaps identified → Next SOP version improved
  → Next Project starts with more knowledge
```

---

## SOP Improvement Protocol

When an SOP needs to be updated:

1. Issue or gap is identified (from post-project review, audit, or user feedback)
2. PM or Buck creates a SOP improvement request (logged in known issues or SOP review tracker)
3. Claude Code updates the SOP: all four layers must stay aligned
4. Updated SOP is tested against current active projects before release
5. Changelog updated; previous version archived

**No SOP update goes live without a review cycle.** Even small changes — if they affect an approval gate, a stop condition, or a required field — must be validated.

---

## What Gets Better Over Time

| Capability | How It Improves |
|-----------|-----------------|
| ROM Budget accuracy | More historical cost data → better unit rates → more accurate budgets |
| Bid leveling | More leveled bids → better sense of what to expect from each trade |
| Vendor intelligence | More project history per vendor → better performance predictions |
| Decision library | More decisions with outcomes → better future guidance |
| Risk flags | More risk patterns learned → AI flags risks earlier |
| SOP quality | More iterations → fewer ambiguities; better employee scripts |
| KPI thresholds | More project data → thresholds calibrated to HCI's actual performance |

---

## Continuous Improvement Cadence

| Activity | Frequency | Owner |
|---------|-----------|-------|
| Post-project review | Every project close | PM + Buck |
| KPI trend review | Monthly | Buck |
| SOP audit | Annual (or after significant issue) | Buck + PM |
| User feedback collection | Ongoing | PM, Superintendent |
| System performance review | Quarterly | Claude Code |
| Historical cost database update | Every project close | AI (auto from final buyout data) |
| Vendor performance update | Every project close | AI (auto from project record) |

---

## What Buck Reviews Annually

At each year-end review, Buck reviews:
1. Company KPI trend for the year
2. Bid win rate and margin trend
3. SOP audit results: which SOPs need updating?
4. Operating Rules Engine: are thresholds still right?
5. Lessons learned: top 5 things we learned this year
6. System roadmap: what should be built next?

---

## The Single Rule of Continuous Improvement

**Every project should improve the company.**  
If a project does not contribute to the knowledge base, it was a missed opportunity regardless of how well it went financially.

---

*Related: SOP 42 (Post-Project Review), Volume 12 (Decision Intelligence), Volume 13 (KPI Intelligence)*  
*Lessons learned service: `03_Source_Code/services/lessons_learned/`*  
*Historical cost service: `03_Source_Code/services/historical_cost/`*
