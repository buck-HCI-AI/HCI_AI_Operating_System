---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD: HCI Role Onboarding System + permanent outbound messaging safety rule
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck authorized building the reusable HCI Role Onboarding System. Include this permanent safety rule in the architecture:

OUTBOUND MESSAGING RULE (NON-NEGOTIABLE)
- The system must never send an outgoing message to anyone outside Hendrickson Construction.
- For external recipients, the system may only create a draft in the authorized user's own email Drafts folder.
- No direct send endpoint may be exposed to any GPT, workflow, n8n process, or agent.
- Internal notifications to approved HCI channels/users may be allowed only through explicitly approved internal messaging paths.
- Every email workflow must default to DRAFT ONLY.
- The created draft must remain linked to the source thread, retain required attachments, preserve provenance, and clearly show intended recipients.
- If the draft cannot be created in the correct user's mailbox, the workflow must fail safely and report the exact problem; it must never reroute or send elsewhere.

Build the HCI Role Onboarding System as a reusable platform component, not an Adam-only form.

Required onboarding flow:
1. Collect identity: name, title, department, manager, projects, visibility scope.
2. Collect responsibilities via multiple choice.
3. Ask: 'With your role, how can HCI AI help you most?' using clickable capability choices tailored to role.
4. Ask user to rank top three time-saving capabilities.
5. Ask workflow preferences: inbox-first, project-first, or daily command center; notification preferences; review requirements; actions that should never be automated.
6. Ask: 'Is there anything else you would want the system to do for you?' Capture as structured feature requests.
7. Generate a proposed role profile: permissions, project scope, enabled capabilities, disabled capabilities, approval rules, dashboard, notifications, requested features.
8. Require admin/Buck approval for any elevated permission; users cannot self-grant authority.
9. Confirm profile with user before activation.
10. Add a 1-week follow-up check-in to capture what is useful, missing, or needs adjustment.

Create a canonical HCI Role Profile Registry with at minimum:
- user name
- role/title
- department
- manager
- project assignments
- visibility level
- enabled capabilities
- disabled capabilities
- approval authority
- preferred dashboard
- notification preferences
- workflow preferences
- requested features
- last review date
- email mailbox used for drafts
- outbound messaging policy status

Use Adam Malmgren as the first implementation profile:
- Senior Project Manager + Executive
- Company-wide project visibility
- Daily Command Center default
- Draft-only email behavior in Adam's own authorized mailbox
- No external direct sends

Acceptance tests:
1. New user completes onboarding and receives a tailored role profile.
2. Elevated permissions remain pending until admin approval.
3. External email request creates a draft only in the correct user's mailbox.
4. No direct send path exists or is callable.
5. Attachments and original thread provenance are preserved.
6. User preferences alter the dashboard/workflow without changing governance.
7. One-week feedback loop is scheduled/recorded.

Return evidence: data model, questionnaire, capability catalog, governance rules, API/schema work, UI/flow, tests, and live Adam onboarding example.
