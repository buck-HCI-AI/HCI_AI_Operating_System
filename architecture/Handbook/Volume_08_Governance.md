# Volume VIII — Governance
*HCI AI Construction Operating System Architecture Handbook*

---

## 8.1 Governance Philosophy
*Authored by: Chief Architect (ChatGPT) — 2026-07-02*

The HCI AI Operating System is governed by a simple principle: AI accelerates decisions, but it does not own them. Construction projects involve contractual obligations, financial commitments, safety responsibilities, and client relationships that remain the responsibility of qualified people. The purpose of governance is not to slow the organization — it is to ensure that every action is performed with the appropriate level of authority.

The platform is designed to remove repetitive administrative work while preserving human accountability where judgment is required. AI continuously analyzes information, identifies risks, recommends actions, prepares documentation, and organizes operational knowledge. Human leaders evaluate those recommendations, apply professional experience, and authorize decisions that affect projects, clients, contracts, or the business.

Governance is implemented through three operational authority tiers.

**Tier 0 — Automated Operations** consist of actions that carry little or no business risk and improve organizational efficiency: monitoring system health, indexing documents, synchronizing approved data between connected systems, generating internal analytics, organizing project information, and producing draft reports or recommendations. These operations may execute automatically because they do not create external commitments or alter approved business records without authorization.

**Tier 1 — Approval-Required Operations** prepare work for human review before execution: uploading finalized project documents to controlled repositories, issuing AI-generated recommendations, drafting client communications, publishing bid analyses, initiating workflow changes, or updating operational records that become part of the project record. These require explicit human review before they become official.

**Tier 2 — Human-Authority Decisions** are never delegated to AI: contractual commitments, financial approvals, vendor selection, award decisions, client commitments, change orders, safety decisions, legal determinations, project execution strategy, personnel decisions, and any action requiring licensed professional judgment or organizational authority. AI may provide supporting analysis, but the decision remains exclusively human.

Every approval, recommendation, and completed action is traceable. The operating system records what information was available, what recommendation was presented, who made the decision, and when the decision occurred. Governance therefore becomes an operational asset rather than an administrative burden, providing transparency, accountability, and organizational learning across every project.

The objective of the governance model is to maximize the speed of routine work while ensuring that responsibility always remains with the people entrusted to build projects, serve clients, and lead Hendrickson Construction. Automation increases capacity. Approval preserves trust. Human judgment remains the final authority.

---

## 8.2 Human Approval Gates (✅ Enforced)

### Never Auto-Execute (Requires Buck Approval)

| Action | Reason | Gate Mechanism |
|--------|--------|---------------|
| HubSpot write-back | External CRM state | GATE-H workflow + approval_queue |
| Email sends to clients | External communication | GATE-E workflow |
| Contract award/commit | Financial commitment | approval_queue |
| Change order approval | Budget impact | executive_inbox |
| Production go-live | System state change | No gate implemented without evidence |
| .env / credentials | Security | Never committed to git |

### AI Acts Autonomously

| Action | Condition |
|--------|-----------|
| Read any data source | Always |
| Generate reports + analysis | Always |
| Write to internal DB tables | Always |
| Create approval queue items | Always |
| Send ntfy notifications | Always |
| n8n workflow triggers | Always (read + analyze) |
| Snapshot persistence | Always |

---

## 8.3 Security Standards (✅ Implemented)

| Standard | Implementation | Status |
|---------|---------------|--------|
| API authentication | `middleware/auth.py` — X-API-Key header on all routes | ✅ |
| .env not in git | .gitignore enforced | ✅ |
| DB credentials from env | No hardcoded passwords anywhere | ✅ |
| API key rotation | Via .env + launchd restart | Manual |
| Token expiry | approve/reject/defer tokens expire | ✅ |
| Audit logging | `platform_audit_log` table | ✅ |

---

## 8.4 Testing Standards (✅ Implemented)

| Standard | Current State |
|---------|-------------|
| New endpoints must have tests before commit | ✅ Enforced |
| Tests run before commit | ✅ Manual — automate via pre-commit hook |
| Test files named `test_{service}.py` | ✅ Convention established |
| Pass rate tracked | ✅ `test_results_*.json` per suite |
| System auditor monitors coverage | ✅ `89% coverage (25/28 services)` |

### Test Suites

| Suite | Tests | Coverage |
|-------|-------|---------|
| test_phase2_intelligence.py | 38 | Ops, Project Brain, Cross-Project |
| test_predictive_engine.py | 21 | Predictive Engine |
| test_system_auditor.py | 11 | System Auditor |
| test_core_services.py | 37 | 20+ core services |
| **Total** | **107** | **89% service coverage** |

---

## 8.5 Database Migration Standards (✅ Implemented)

| Standard | Convention |
|---------|-----------|
| Migration files | `05_Database/migrations/NNN_description.sql` |
| Sequential numbering | 001 → 014 (current) |
| Applied manually | `docker exec hci_postgres psql ... < migration.sql` |
| Idempotent | All use `CREATE TABLE IF NOT EXISTS`, `ON CONFLICT DO UPDATE` |
| Rollback | Manual — no automated rollback |

---

## 8.6 Architecture Review Process (✅ Partial)

| Process | Status |
|---------|--------|
| Architecture Review Cycle (ARC) template | ✅ `ACR_TEMPLATE.md` at repo root |
| ACR-004 review completed | ✅ `ACR-004-ARCHITECTURE-REVIEW.md` |
| System Auditor generates daily architecture flags | ✅ `/api/v1/services/system-auditor/run` |
| ADR tracking | ✅ `Architecture/ADRs/` (5 ADRs) |
| Handbook sync after implementation | ✅ This document |

---

## 8.7 Coding Standards (✅ Enforced via CLAUDE.md)

- No explanatory comments unless WHY is non-obvious
- No trailing summaries in responses
- Prefer editing existing files over creating new ones
- `.command` files on Desktop for shell commands Buck must run
- No hardcoded passwords
- DB credentials always from environment variables
- Security: never expose internal stack traces

---

## 8.8 Sections Requiring Chief Architect Input (⚠️)

### 8.8.1 Release Management Process
*[Chief Architect: How should the platform transition from local-only to production/cloud?
Define staging, testing, and release gate criteria.]*

### 8.8.2 Continuous Deployment Vision
*[Chief Architect: Define the target CD pipeline for the platform]*

### 8.8.3 Operational Governance as the Platform Scales
*[Chief Architect: How does governance evolve when the platform manages more projects or companies?]*
