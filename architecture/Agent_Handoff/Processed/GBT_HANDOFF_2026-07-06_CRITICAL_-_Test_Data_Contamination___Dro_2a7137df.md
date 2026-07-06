---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: CRITICAL - Test Data Contamination + Dropped Telegram Messages - Fix Before Onboarding
created_at: 2026-07-06
summary: Handoff from ChatGPT via GBT Gateway
---

Mission Control still shows production-facing test data contamination and messaging reliability concerns that must be fixed before onboarding. Investigate and remediate: (1) false/test risk records contaminating production health, especially 101 Francis project_id=2 risk_code=schedule_variance GATE2-TS02b steel-delay artifact; (2) any other sandbox/test data leaking into live Mission Control, Project Brain, risks, directives, daily logs, or schedule variance tables; (3) dropped/skipped Telegram or ai_messages deliveries, including prior skipped messages, so material updates reliably reach Buck/agents through the Telegram primary channel. Produce a verified cleanup report with affected tables/records, actions taken, tests run, and remaining blockers before onboarding proceeds.
