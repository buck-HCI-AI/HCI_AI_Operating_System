---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: BUILD + PILOT: Multi-hat HCI onboarding with Buck as first test user
created_at: 2026-07-10
summary: Handoff from ChatGPT via GBT Gateway
---

Buck authorized building the HCI multi-hat onboarding/profile system and using Buck as the first pilot user.

Core model:
- Do not rely on a single job title. Capture the hats each person wears (e.g., Executive, PM, Superintendent, Accounting, Estimating, Field, Business Development, AI Development).
- Capabilities are composed from hats; permissions remain governed separately.
- Generate a tailored welcome/introduction for each user based on identity, hats, projects, responsibilities, enabled capabilities, and restrictions.

Immediate security rule:
- AI-building / AI-system-development capabilities must be restricted to Buck only for now.
- No other user may access architecture/build/admin capabilities unless Buck explicitly approves later.
- Enforce this in the role/capability registry and test it.

Pilot user profile:
- Buck Adams
- Hats: PM, Superintendent, Executive/Operations, HCI-AI Owner/Builder
- Active project responsibilities: 101F and 1355R
- Company role: PM/Superintendent at Hendrickson Construction; owner/operator of HCI-AI (do not label Buck as owner of Hendrickson Construction)
- Dashboard should blend executive, PM, field, and AI-development views.

Tailored welcome guide requirements:
- Who the user is in the system
- Hats selected
- Assigned/visible projects
- What the system can do today
- What it cannot do
- Approval boundaries
- Enabled capabilities
- Preferred dashboard
- Example prompts tailored to the user's work
- How to request new capabilities

Continuous-learning requirement:
- Capture actual user questions that the system cannot fulfill across all roles.
- Store each unmet request with: user, hat/role, project, request text, attempted capability, failure reason, source/tool limitation, urgency, workaround, and whether it suggests a new reusable capability.
- Aggregate recurring unmet needs across SS, PM, executive, accounting, estimating, and office users.
- Surface patterns to the roadmap instead of losing them in chat history.
- Ask a lightweight follow-up such as: 'Did this answer your need?' and, when not, 'What should the system have done instead?'

Acceptance tests:
1. Buck completes onboarding and receives a tailored multi-hat profile and welcome guide.
2. Buck sees executive + PM + SS + AI-development capabilities.
3. A non-Buck test user cannot access AI-building/admin capabilities.
4. An unmet field question is captured in the learning registry with context and appears in a roadmap/needs report.
5. Updating hats changes dashboard/capabilities without changing permissions automatically.
6. Governance boundaries remain intact.

Deliverables:
- Data model / role profile registry updates
- Onboarding questionnaire
- Tailored welcome guide generator
- Capability/permission logic
- Unmet-needs learning registry + reporting
- Buck pilot evidence
- Regression tests and blockers
