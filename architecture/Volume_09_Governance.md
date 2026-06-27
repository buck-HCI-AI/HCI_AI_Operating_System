# Volume IX — Governance
*HCI AI Construction Operating System Architecture Handbook*

---

## 9.1 Governance Philosophy (⚠️ Chief Architect Input Required)

*[Chief Architect: Define the governance philosophy — how does Hendrickson Construction balance
AI autonomy with human oversight? What is the long-term vision for AI governance as capability grows?]*

---

## 9.2 Human Approval Gates (✅ Enforced)

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

## 9.3 Security Standards (✅ Implemented)

| Standard | Implementation | Status |
|---------|---------------|--------|
| API authentication | `middleware/auth.py` — X-API-Key header on all routes | ✅ |
| .env not in git | .gitignore enforced | ✅ |
| DB credentials from env | No hardcoded passwords anywhere | ✅ |
| API key rotation | Via .env + launchd restart | Manual |
| Token expiry | approve/reject/defer tokens expire | ✅ |
| Audit logging | `platform_audit_log` table | ✅ |

---

## 9.4 Testing Standards (✅ Implemented)

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

## 9.5 Database Migration Standards (✅ Implemented)

| Standard | Convention |
|---------|-----------|
| Migration files | `05_Database/migrations/NNN_description.sql` |
| Sequential numbering | 001 → 014 (current) |
| Applied manually | `docker exec hci_postgres psql ... < migration.sql` |
| Idempotent | All use `CREATE TABLE IF NOT EXISTS`, `ON CONFLICT DO UPDATE` |
| Rollback | Manual — no automated rollback |

---

## 9.6 Architecture Review Process (✅ Partial)

| Process | Status |
|---------|--------|
| Architecture Review Cycle (ARC) template | ✅ `ACR_TEMPLATE.md` at repo root |
| ACR-004 review completed | ✅ `ACR-004-ARCHITECTURE-REVIEW.md` |
| System Auditor generates daily architecture flags | ✅ `/api/v1/services/system-auditor/run` |
| ADR tracking | ✅ `Architecture/ADRs/` (5 ADRs) |
| Handbook sync after implementation | ✅ This document |

---

## 9.7 Coding Standards (✅ Enforced via CLAUDE.md)

- No explanatory comments unless WHY is non-obvious
- No trailing summaries in responses
- Prefer editing existing files over creating new ones
- `.command` files on Desktop for shell commands Buck must run
- No hardcoded passwords
- DB credentials always from environment variables
- Security: never expose internal stack traces

---

## 9.8 Sections Requiring Chief Architect Input (⚠️)

### 9.8.1 Release Management Process
*[Chief Architect: How should the platform transition from local-only to production/cloud?
Define staging, testing, and release gate criteria.]*

### 9.8.2 Continuous Deployment Vision
*[Chief Architect: Define the target CD pipeline for the platform]*

### 9.8.3 Operational Governance as the Platform Scales
*[Chief Architect: How does governance evolve when the platform manages more projects or companies?]*
