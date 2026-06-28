---
source_agent: ChatGPT
destination_agent: Claude Code
document_type: implementation_request
priority: high
status: pending
related_system: 
title: HCI AI OS — Priority 4 & 6 Configuration, Integration, and Production Readiness
created_at: 2026-06-28
summary: Handoff from ChatGPT via GBT Gateway
---

EXECUTION DIRECTIVE — HIGH PRIORITY

Implement the combined Priority 4 (Configuration & Integration) and Priority 6 (Production Readiness) workstreams as one coordinated implementation package. The objective is to complete production-grade integrations, operational hardening, security, observability, and deployment readiness while preserving the existing governance model.

PRODUCTION READINESS

Implement:
- Automated backups for critical data stores and configuration.
- Disaster recovery plan with documented recovery procedures and validation.
- Health monitoring with automatic service restart where appropriate.
- Audit log validation to ensure critical events are recorded and verifiable.
- Load testing across all gateway endpoints with documented results.
- Gateway failover strategy and implementation where feasible.
- Security review covering authentication, authorization, rate limiting, and secret management.
- Production logging with structured logs and retention guidance.
- Monitoring dashboards for system health, services, workflows, gateway, and integrations.

CONFIGURATION & INTEGRATION

HubSpot:
- Complete associations
- Timeline synchronization
- Deal stage synchronization
- Tasks
- Companies
- Contacts
- Notes
- Attachments

Google Drive:
- Metadata indexing
- Folder intelligence
- Automatic tagging
- Duplicate detection

Outlook / Microsoft 365:
- Inbound classification
- Meeting extraction
- Commitment tracking
- Daily summaries

Google Sheets:
- Template registry
- Automatic validation
- Bid imports
- Budget synchronization

Houzz:
- Complete extraction of designed tables
- Images
- Selections
- Client portal data
- Change history

Authentication:
Implement role-based permissions for:
- Project Manager
- Estimator
- Executive
- Owner
- Accounting
- Field
- Read-only
- API clients

Gateway:
Expose appropriate endpoints for:
- Operations Manual
- Architecture documentation
- Knowledge search
- Mission Control
- Workflow analytics
- AI Memory

Implementation Requirements:
- Preserve all governance, approval gates, and human-in-the-loop controls.
- Follow existing FastAPI, PostgreSQL, gateway, n8n, Project Brain, and documentation conventions.
- Add database migrations, configuration schemas, gateway endpoints, tests, and documentation updates as needed.
- Validate security-sensitive changes before completion.

Deliverable:
Create PRIORITY_4_6_PRODUCTION_READY.md documenting implementation summary, configuration changes, integrations completed, security review, production readiness checklist, gateway/load test results, monitoring coverage, remaining gaps, and recommended next steps.
