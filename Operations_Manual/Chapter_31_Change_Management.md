# Chapter 31 — System Updates & Change Management
*HCI AI Operations Manual — Part III: Governance*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 31.1 Two Types of Changes

**Operational changes** — changing how the business runs (new SOP, new approval workflow, new role access). These require GBT + Buck alignment.

**Technical changes** — changing the software (new API endpoint, DB schema, n8n workflow). These are Claude Code's domain.

Both types require the same discipline: document before doing, verify after doing, update the handbook and changelog.

---

## 31.2 Architecture Freeze v1.0

As of **2026-06-28**, the core schema is locked.

**What this means:**
- Existing table schemas cannot be modified without an ACR (Architecture Change Request)
- New tables require an ACR
- Existing endpoint contracts cannot break (GBT depends on them)
- New endpoints are additive and don't require ACR

**What does NOT require an ACR:**
- Adding columns with defaults (non-breaking)
- Adding indexes
- Adding new API endpoints
- New n8n workflows
- Bug fixes that don't change API contracts

**What DOES require an ACR:**
- Dropping tables or columns
- Renaming tables or columns
- Changing endpoint response structure
- Adding authentication to currently-open endpoints
- Changing core data models (project health scoring, risk types, etc.)

---

## 31.3 ACR Process

**File an ACR when schema change is needed:**

1. Create ACR document: `architecture/ACRs/ACR-00X-Title.md`
2. Format:
```markdown
# ACR-00X — [Title]
**Date:** YYYY-MM-DD
**Filed by:** [Claude Code / GBT]
**Status:** Proposed

## Motivation
Why is this change needed?

## Proposed Change
What exactly changes (table, column, endpoint)?

## Impact Analysis
What breaks? What needs to be updated? What GBT endpoints are affected?

## Migration Plan
How do we migrate existing data?

## Decision
[ ] Approved by: GBT + Buck Adams
[ ] Date:
```

3. Post handoff to GBT: `POST /gateway/agent/handoff` with ACR document
4. GBT reviews and approves/rejects
5. Buck final confirmation for any data-destructive changes
6. Claude Code implements after approval
7. Update ACR status to COMPLETE

---

## 31.4 Code Change Protocol

**For any code change (Claude Code):**

1. **Read the file** before editing — never edit blind
2. **Test after change** — the relevant endpoint or feature must work
3. **Reload uvicorn** if FastAPI changed: `kill -HUP $(pgrep -f "uvicorn main:app")`
4. **Verify via curl** that the endpoint returns expected results
5. **Update handbook** if the change adds or modifies a documented capability
6. **Update CHANGELOG.md** with the change
7. **Update this Operations Manual** if the change affects operations procedures

---

## 31.5 Database Migration Protocol

**Before any migration:**
```bash
# Backup first (always)
docker exec hci_postgres pg_dump -U hci_admin hci_os > \
  "/Volumes/HCI_AI_DEV /backups/db/pre_migration_$(date +%Y%m%d_%H%M%S).sql"
echo "Backup complete"
```

**Migration naming:** `migration_018_description.sql`, `migration_019_description.sql`...

**Apply migration:**
```bash
docker exec -i hci_postgres psql -U hci_admin -d hci_os < 05_Database/migrations/migration_018_description.sql

# Verify
docker exec hci_postgres psql -U hci_admin -d hci_os -c "\d new_table_name"
```

**Rollback:** Migrations must include rollback SQL or explicit rollback instructions.

---

## 31.6 n8n Workflow Change Protocol

1. Make changes in n8n UI
2. Test the workflow (Execute Now in n8n)
3. Verify expected output
4. Export workflow: n8n UI → ⋮ → Export JSON
5. Save to `03_Source_Code/workflows/n8n/{WORKFLOW_NAME}.json`
6. Update Chapter 20 (n8n Workflow Management) with any schedule or behavior changes
7. Update CHANGELOG.md

---

## 31.7 GBT-Initiated Changes

GBT (Chief Architect) requests changes via `/gateway/agent/handoff`. Claude Code receives these and acts on them in the next session.

**Claude Code's response to handoffs:**
1. Read the handoff from `architecture/Agent_Handoff/Inbox/`
2. Understand the request fully — ask Buck if unclear
3. Implement with the same rigor as any other change
4. Test and verify
5. Post response handoff: `POST /gateway/agent/handoff` with status: "COMPLETE"
6. Update GBT via handoff or Buck relays the completion

**GBT cannot directly modify code or database.** GBT's authority is architecture and philosophy. Implementation always goes through Claude Code.

---

## 31.8 Changelog Protocol

Every significant change gets documented in `architecture/CHANGELOG.md`.

Entry format:
```markdown
## v{version} — {date}

### Built
- [Feature] Description

### Fixed
- [Bug] Description

### Changed
- [Change] What changed and why

### Blocked
- [Block] What's blocked and why
```

Version numbering: `{major}.{minor}` — increment minor for features, minor.patch for fixes. Major for architectural changes.

---

## 31.9 Communication Protocol (AI Team Changes)

| Scenario | Claude Code Action | GBT Action |
|----------|------------------|-----------|
| New feature needed | Build it, document it, post handoff to GBT with result | Review, validate, add to handbook |
| Architecture question | Post handoff asking for GBT decision | Reply with architectural direction |
| Bug found + fixed | Fix it, update changelog, notify Buck via ntfy | N/A (ops issue) |
| ACR needed | File ACR, post handoff | Approve/reject ACR |
| Handbook chapter ready for philosophy content | Post handoff with chapter skeleton + placeholders | Author the philosophy sections |

---

*Cross-reference: Chapter 17 (Architecture), Chapter 23 (Backup), Chapter 27-28 (Governance)*
