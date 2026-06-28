---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: Implement HCI Mobile Command Center with ntfy Notifications
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

Objective: Design and implement mobile approval notifications using ntfy integrated with the existing HCI approval architecture.

Requirements:
1. Integrate ntfy (self-hosted or ntfy.sh configurable) into the notification layer.
2. Use n8n to publish notifications whenever high-priority approval queue items are created.
3. Notification payload should include project, approval type, amount (if applicable), risk level, recommendation, and deep link.
4. Deep links should open either the HCI approval dashboard or ChatGPT conversation for review before approval.
5. Preserve the existing human-in-the-loop governance model. Notifications must never auto-approve or trigger production writes.
6. Support notification categories (Critical, High, Normal) and quiet hours configuration.
7. Store ntfy configuration in environment variables and document deployment steps.
8. Add audit logging for notification delivery attempts and failures.
9. Produce architecture documentation and implementation notes for the mobile command center.
10. Ensure compatibility with Gate 5 Architecture Freeze v1.0.
