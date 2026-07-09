---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: medium
status: pending
related_system: 
title: Field/PM/Management Operating Model Report for HCI AI Construction OS
created_at: 2026-07-08
summary: Handoff from ChatGPT via GBT Gateway
---

Buck asked for a full report on how the HCI AI Construction OS should function for field operations, report owners, management, and ownership. I drafted the operating model below. Please review against current repo/manual/implementation state and use it as an input for documentation/onboarding/system design alignment.

# HCI AI Construction OS
## Operating Model for Field Operations, Project Management, Leadership, and Ownership

Based on the system architecture, the live gateway, and the work completed to date, this is how I believe the finished HCI AI Operating System should function when fully operational.

## Primary Philosophy

The AI should never become another software package employees have to maintain.

Instead, the AI should quietly maintain the company's operational intelligence while people continue building projects.

Every person should only receive information they actually need.

Nobody should have to hunt for information.

## Level 1 — Field Operations
### Superintendent / Field PM

This is where information originates.

The field should only worry about construction.

### Daily Workflow

Morning:

The Field GPT should immediately answer:

- What is today's schedule?
- What inspections are due?
- What materials should arrive?
- What subcontractors are expected?
- Weather impacts
- Critical safety reminders
- Outstanding RFIs affecting today's work
- Long-lead items requiring follow-up

No searching.
No opening five programs.
Just ask.

During the day:

The superintendent simply talks.

Example:

> We poured footing 3 today. Concrete finished at 2:30. Steel delivery delayed until Friday. Electrician discovered missing conduit sleeves. Need RFI.

The AI automatically creates:

- Daily Log
- Progress Update
- Delay Record
- Potential RFI
- Schedule Impact
- Lessons Learned candidate
- Owner notification, if required

without duplicate entry.

### Field Photos

Pictures automatically become:

- Progress documentation
- Percent complete
- Quality control
- Potential punch items
- Safety documentation

linked to:

- Project
- Drawing
- Location
- Date
- Trade

### End of Day

Instead of writing reports, Field GPT asks: "What happened today?"

The superintendent answers naturally. Everything else is generated.

## Level 2 — Project Manager

PMs should not spend their day collecting information. The system should already know.

Morning dashboard:

- Project health
- Budget
- Schedule
- Risks
- Outstanding RFIs
- Submittals
- Procurement
- Open change orders
- Pending owner decisions
- Bid activity

Every item should be clickable.

### PM AI

Example questions:

- Show me everything delaying Division 6.
- Which subcontractors have not answered?
- Who needs follow-up today?
- Which bids are abnormal?
- Which RFIs are affecting schedule?
- What owner decisions are overdue?

Everything should already be correlated.

### Automatic PM Reports

Weekly PM Review:

- Budget variance
- Schedule variance
- Procurement status
- Risk register
- Upcoming milestones
- Client issues
- Open approvals
- Recommendation list

No manual report writing.

## Level 3 — Executive Management

Management should not receive daily noise. They receive trends.

Morning Executive Report, generated automatically:

- Company health
- Project health
- Critical risks
- Financial exposure
- Schedule exposure
- Cash flow
- Procurement
- Pending decisions
- Staff workload
- Subcontractor performance
- AI recommendations

One report. Five minutes.

### Exception Reporting

Management only gets interrupted when something matters:

- Schedule slips
- Budget overruns
- Large bid spreads
- Critical RFIs
- Permit delays
- Long-lead procurement
- Major safety issue
- Subcontractor bankruptcy
- Client dissatisfaction

Everything else stays silent.

## Level 4 — Owner / Chris Hendrickson

Chris should never need to ask, "What's going on?" The AI should already know.

Owner dashboard:

- Company health
- Revenue
- Pipeline
- Bid status
- Profitability
- Risk exposure
- Cash flow
- Labor loading
- Backlog
- Future work

One screen.

Owner questions:

- Which projects concern you?
- Which PM needs help?
- Which superintendent is overloaded?
- How much risk exists next quarter?
- What jobs are falling behind?
- Which vendors are performing best?
- Show me every owner decision waiting.

## Level 5 — Buck

Buck is different. Buck is running both construction operations and the AI platform.

His dashboard should include everything above plus:

- AI health
- Connector health
- Gateway health
- Workflow status
- Automation failures
- Pending approvals
- Repository health
- AI communication status
- Model performance
- Knowledge growth

Because Buck is effectively operating the operating system itself.

## Background Automation

Nobody sees this.

The AI continuously performs:

- Reads email
- Reads HubSpot
- Reads Houzz
- Reads Google Drive
- Reads drawings
- Reads specifications
- Reads RFIs
- Reads ASIs
- Reads submittals
- Reads schedules
- Reads daily logs
- Reads bid folders
- Reads meeting minutes
- Updates project memory
- Updates vendor memory
- Updates lessons learned
- Updates cost history
- Updates procurement intelligence
- Updates schedule intelligence
- Updates executive intelligence

Continuously.

## Cross-Project Intelligence

The real value is learning across every project, not just understanding one job.

Examples:

- Which framing subcontractor finishes fastest?
- Average Division 7 cost?
- Typical plumbing cost per square foot?
- Average permit duration in Aspen?
- Which vendors consistently finish late?
- Which roofing details usually generate RFIs?
- Typical electrical bid spread?
- Which architects produce the fewest RFIs?

This becomes institutional knowledge.

## AI Memory

Every project develops its own brain, including:

- History
- Meetings
- RFIs
- Drawings
- Lessons
- Decisions
- Photos
- Costs
- Communications
- Vendor history
- Daily logs

When someone new joins a project, they can be productive almost immediately because the AI already knows the project's history.

## Approval Philosophy

Nothing important happens automatically.

AI recommends. Humans approve.

Especially:

- Emails
- Contracts
- Budget changes
- Award decisions
- Owner commitments
- Client communication
- Anything external

## Notifications

The AI should avoid becoming spam.

Preferred pattern:

- Daily digest
- Weekly digest
- Critical alerts
- Monthly executive summary

Everything else remains searchable.

## End State

When this system is mature:

- The superintendent spends more time building and less time documenting.
- The PM spends more time managing and less time assembling reports.
- Leadership spends more time making decisions and less time requesting updates.
- The owner has real-time visibility into the entire company.
- Institutional knowledge no longer disappears when an employee leaves.

## Current-State Assessment from GBT

From live system checks I verified, the architecture is already aligned with much of this vision. The gateway exposes project PM consoles, executive reporting, project brains, drift checking, cost forecasting, procurement, approvals, and messaging. The remaining work appears to be operational maturity rather than inventing new concepts: ensure connector freshness, expand cross-project intelligence access to GBT, complete documentation, and validate that every workflow executes reliably.

The result should be an operating system that supports construction rather than another administrative system that the construction team has to support.

Please review this for consistency with the current manual, field GPT instructions, onboarding materials, and live endpoint capabilities. Flag mismatches and convert into a durable architecture/onboarding artifact if appropriate.
