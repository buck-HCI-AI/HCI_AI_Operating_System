# Chapter 16 — Project Close-Out
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-07-01*

---

## 16.1 Overview

Close-out is where a project stops being "active work" and becomes "company knowledge." Done well, everything learned on this job — good vendors, bad vendors, accurate costs, mistakes worth not repeating — becomes available to every future project. Done poorly, the same lessons get relearned at full cost on the next job.

A project is not done when the punch list is signed off. It's done when its knowledge has been captured back into the system.

---

## 16.2 Close-Out Triggers

Close-out begins when:
- Substantial completion has been achieved and accepted by the owner
- Punch list is substantially complete
- Final Pay Application is submitted

The project's status transitions through the system's lifecycle states:
```
active → closeout → completed
```
```
GET /gateway/projects?status=closeout
```
lists everything currently in close-out, so nothing sits half-finished without visibility.

---

## 16.3 The Close-Out Checklist

**Financial close-out:**
- Final Pay Application reviewed and processed
- Unconditional final lien waivers collected from every sub (Chapter 07 §7.7) — **retention is never released without these**
- All back charges resolved and documented
- Final budget vs. actual reconciliation — contract value vs. total committed vs. total paid

**Documentation close-out:**
- As-built drawings collected and filed
- Warranty documents and O&M manuals collected from every sub with warrantable work
- Final submittal log confirmed complete (Chapter 13) — no `pending`/`under_review` items left open
- All RFIs closed (Chapter 15) — no `open` items left on the register

**Client close-out:**
- Final walkthrough with the client
- Warranty period start date communicated to the client
- Client sign-off documented

---

## 16.4 Lessons Learned — Feeding the Knowledge Graph

This is the step that makes close-out worth doing carefully. Every project generates real intelligence that the next project shouldn't have to rediscover:

```
POST-equivalent: lessons_learned table entries, per project
GET /gateway/knowledge/lessons?category={category}&csi={csi_division}
```

**What gets captured:**
- Vendor performance — who delivered on time and on budget, who didn't (feeds `vendor_intelligence` and cross-project vendor scoring — see Chapter 06)
- Cost accuracy — how the final numbers compared to the original estimate, by CSI division (feeds `historical_cost_records` and future ROM estimates — Chapter 14 §14.6)
- Scope/design issues — anything that caused an RFI storm, a change order cluster, or a schedule slip that a future project could avoid by catching it earlier
- What worked — processes, subs, or sequencing decisions worth repeating

This is not optional paperwork. A project that closes out without lessons-learned entries is a project whose knowledge dies with it. 655 South Garmisch's 21 historical cost records and 7 lessons-learned entries are the model — every closed project should add to that base, not just 655 Garmisch.

---

## 16.5 Archiving

Once financial, documentation, and client close-out are all complete:

```
Project status → 'completed'
```

At this point the project moves from "live operational data" to "reference" in system terms — it stops appearing in active dashboards (executive report, mission control, role consoles all filter to `active`/`design`/`bidding`/`preconstruction`) but remains fully queryable for historical/knowledge purposes. Nothing gets deleted — see Chapter 22 for data retention policy.

---

## 16.6 Final Reports

At close-out, generate and file:
- Final financial summary (contract value, total committed, total paid, any variance)
- Final schedule summary (planned vs. actual completion, cause of any variance)
- Lessons-learned summary (the entries logged in §16.4, consolidated into one document)

These go in the project's Drive folder → `Closeout/` subfolder, and a copy of the financial and schedule summary goes to Buck for the record.

**What NOT to do:**
- Do not release final retention before unconditional lien waivers are in hand from every sub.
- Do not skip lessons-learned entries because the project "went fine" — the projects with no surprises are exactly the ones whose cost and vendor data are most reliable for future estimates.
- Do not mark a project `completed` while RFIs or submittals are still open — resolve or explicitly close them out first.

---

*This completes Part I — Business Operations. See Part II (Chapter 17 onward) for how the AI system itself is operated, monitored, and maintained.*
