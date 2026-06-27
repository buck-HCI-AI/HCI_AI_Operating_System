# Gate Audit Log — HCI AI Operating System

**Purpose:** Immutable audit trail for all AI action approvals and denials.
**AUTO-025 | Sprint 2 — Registry Consolidation**

## Structure

```
logs/gates/
  YYYY-MM-DD-gate-H-hubspot-write.jsonl   # Gate H: HubSpot write approvals
  YYYY-MM-DD-gate-G-pr-merge.jsonl        # Gate G: PR merge notifications
  YYYY-MM-DD-gate-E-client-comms.jsonl    # Gate E: Client communication approvals
  YYYY-MM-DD-gate-F-financial.jsonl       # Gate F: Financial action approvals
  YYYY-MM-DD-gate-HZ-H1-houzz.jsonl      # Gate HZ-H1: Houzz write approvals
```

## Log Entry Format (JSONL)

```json
{
  "timestamp": "2026-06-27T03:00:00Z",
  "gate": "H",
  "action_type": "hubspot_write",
  "actor": "hubspot_miner",
  "target": "contact:12345",
  "proposed_payload": {},
  "decision": "queued_for_human_approval",
  "approval_queue_id": 42,
  "authorized_by": null
}
```

## Rules

- Append-only — no deletions, no overwrites
- One file per gate per day (rotated at midnight by n8n)
- Decisions: `queued_for_human_approval` | `approved` | `denied` | `auto_denied`
- Human approvals recorded with `authorized_by: "Buck Adams"`
