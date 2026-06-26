# Read-Only and Approval Controls

**MVP Sprint 1 — Safety Architecture**  

---

## Core Principle

The HCI AI system NEVER writes to any external system or production database table without explicit Buck approval. Every proposed write action passes through the approval queue first.

---

## Control Layers

### Layer 1: Read-Only Connectors

All connector registry entries start with `read_only=TRUE`. Write access requires:
1. QA gate passage for that workflow
2. Explicit Buck approval to flip the connector to write mode

### Layer 2: Dry-Run Default

All write-capable endpoints default to `dry_run=true`:
- Returns the proposed payload and intelligence analysis
- Zero writes to any table
- Response includes `"mode": "dry_run"` confirmation

### Layer 3: Approval Queue

When `dry_run=false`, the action is NOT executed — it is queued:

```
enqueue() → status='pending' → Buck reviews → approve() → mark_executed()
```

Status progression:
- `pending` — no system changed
- `approved` — Buck has approved, still not executed
- `executed` — caller has applied the change and marked complete
- `rejected` — Buck rejected, no change ever made

The system NEVER auto-advances from `approved` to `executed`.

### Layer 4: Audit Trail

Every queue action (enqueue, approve, reject, execute) writes to `platform_audit_log` with:
- `event_type` — action.queued / action.approved / action.rejected / action.executed
- `actor` — who took the action
- `entity_id` — approval_queue row ID
- `summary` — human-readable description
- `correlation_id` — UUID linking all audit records for one action

---

## What Always Requires Human Approval

| Action Type                     | System       | Rule                              |
|---------------------------------|--------------|-----------------------------------|
| HubSpot deal/contact update     | HubSpot      | Always queued, never auto-written |
| Google Drive file write/move    | Drive        | Test folder only until approved   |
| Houzz project update            | Houzz        | Draft only until approved         |
| Daily log write to DB           | PostgreSQL   | Queued when dry_run=false         |
| Bid package write to DB         | PostgreSQL   | Queued when dry_run=false         |
| Client-facing communication     | Email/Houzz  | Always requires human approval    |
| Bid award, contract, change order | Any        | Always requires human approval    |
| Financial commitment            | Any          | Always requires human approval    |

---

## Rollback Path

Every approval queue entry includes a `rollback_path` field specifying how to undo the action if needed. This is required for any action that modifies structured data.

---

## DB Tables

| Table             | Purpose                                               |
|-------------------|-------------------------------------------------------|
| `approval_queue`  | Holds all pending/approved/rejected/executed actions  |
| `connector_registry` | Tracks read_only status per project per source     |
| `platform_audit_log` | Immutable audit trail for all system actions       |
