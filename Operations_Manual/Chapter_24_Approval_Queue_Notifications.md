# Chapter 24 — Approval Queue & Notification System
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 1.0 | **Date:** 2026-06-30

---

## 24.1 How the Approval Loop Works

Every action the AI system wants to take in the outside world — sending an email, updating a HubSpot record, approving a bid — goes through the approval queue. The queue is how the system asks Buck "is this OK?"

```
AI generates proposed action
        ↓
  approval_queue INSERT (status: 'pending_approval')
        ↓
  ntfy push to Buck's phone
        ↓
  Buck sees notification → opens link → reviews proposed action
        ↓
  [APPROVE] or [REJECT]
        ↓
  APPROVE → appropriate GATE webhook fires → action executes
  REJECT  → record closed, AI notified
```

**Buck is always the last gate.** Nothing executes in the outside world without his approval.

---

## 24.2 Approval Queue Table

```sql
TABLE approval_queue (
    id                INTEGER PRIMARY KEY,
    action_type       TEXT,       -- 'hubspot_write', 'email_send', 'file_upload', 'bid_award', etc.
    project_id        INTEGER,    -- FK to projects (NOT project_code)
    status            TEXT,       -- 'pending_approval', 'approved', 'rejected', 'void'
    proposed_payload  JSONB,      -- all details including 'amount', 'title', 'body'
    approved_by       TEXT,
    approved_at       TIMESTAMP,
    rejection_reason  TEXT,
    created_at        TIMESTAMP DEFAULT NOW()
)
```

**Critical schema notes:**
- NO `amount` column — amount is in `(proposed_payload->>'amount')::numeric`
- NO `project_code` column — use `project_id` (integer) to join `projects`
- `change_orders` is NOT a separate table — lives in `approval_queue WHERE action_type ILIKE '%change_order%'`

---

## 24.3 Current Queue State

Check pending items:
```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "
SELECT id, action_type, project_id, status, created_at,
       (proposed_payload->>'title') as title,
       (proposed_payload->>'amount') as amount
FROM approval_queue
WHERE status = 'pending'
ORDER BY created_at DESC
LIMIT 20;"
```

Queue counts:
```bash
docker exec hci_postgres psql -U hci_admin -d hci_os -c "
SELECT status, count(*) FROM approval_queue GROUP BY status ORDER BY count DESC;"
```

**Status values:** `pending` (1,039 active) | `void` (204 cleaned) | `executed` (59) | `approved` (20) | `rejected` (7)

**Important:** Status is `'pending'` NOT `'pending_approval'` — the actual value used in all queries and code.

---

## 24.4 Approval Gates

Each gate type triggers a different downstream action when approved:

| Gate | Workflow | Trigger URL | Action |
|------|---------|------------|--------|
| GATE-H | HubSpot writes | n8n webhook | Updates contact/deal/note in HubSpot |
| GATE-E | Email sends | n8n webhook | Sends email from Buck's Outlook |
| GATE-F | File operations | n8n webhook | Creates/uploads file to Drive |
| GATE-G | GitHub pushes | n8n webhook | Approves and pushes to repository |

**Gate workflow IDs:** In n8n — GATE-H.json, GATE-E.json, GATE-F.json, GATE-G.json

---

## 24.5 Creating an Approval Item (Programmatic)

Via gateway API:
```bash
curl -X POST "https://speculate-armband-retinal.ngrok-free.dev/gateway/approvals" \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "hubspot_write",
    "project_id": 3,
    "title": "Update 1355R deal stage to Awarded",
    "body": "Proposed change: move deal 321351275210 from In Review to Awarded",
    "amount": null,
    "priority": "normal"
  }'
```

Via Python:
```python
import requests
r = requests.post(
    "https://speculate-armband-retinal.ngrok-free.dev/gateway/approvals",
    headers={"X-API-Key": "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"},
    json={
        "action_type": "bid_award",
        "project_id": 3,
        "title": "Award concrete to Pacific Concrete Inc",
        "amount": 185000,
        "body": "Recommended award: Pacific Concrete Inc, $185,000, 1355 Riverside Div 03"
    }
)
```

---

## 24.6 ntfy Notification System

**Topic:** `hci-ai-os-buck`  
**URL:** `https://ntfy.sh/hci-ai-os-buck`  
**App:** ntfy on Buck's iPhone

### Notification Priority Levels

| Priority | When Used | Sound |
|----------|----------|-------|
| urgent | RED project, critical risk, security alert | Loud, insistent |
| high | Approval needed, YELLOW project change | Normal alert |
| default | Informational (morning brief delivered, etc.) | Quiet |
| low | Background sync complete, audit passed | Silent |

### Sending a Manual ntfy Notification

```bash
curl -X POST "https://ntfy.sh/hci-ai-os-buck" \
  -H "Title: Test Notification" \
  -H "Priority: default" \
  -H "Tags: white_check_mark" \
  -d "This is a test from the HCI AI OS."
```

### Via Gateway Batch Endpoint

```bash
curl -X POST "https://speculate-armband-retinal.ngrok-free.dev/gateway/batch" \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{
    "operations": [{
      "type": "ntfyPush",
      "title": "1355R — Concrete SOW Ready for Review",
      "body": "3 SOW drafts created and in your Outlook drafts folder.",
      "priority": "high"
    }]
  }'
```

---

## 24.7 ntfy Issue (Known — Under Monitoring)

**Symptom:** Push notification arrives (phone buzzes) but messages don't appear in ntfy app.  
**Likely cause:** Server URL mismatch after re-subscribe — ntfy app may be pointing to wrong topic.  
**Current status:** Buck monitoring with GBT.  
**Workaround:** Check ntfy.sh/hci-ai-os-buck in a browser to see messages even if app doesn't show them.

---

## 24.8 Voiding Duplicate or Stale Queue Items

During BTW sprint, 204 duplicate approval items were voided. To void stale items:
```sql
-- Void specific item
UPDATE approval_queue SET status = 'void', rejection_reason = 'duplicate'
WHERE id = {id};

-- Void all items older than 30 days that are still pending
UPDATE approval_queue 
SET status = 'void', rejection_reason = 'expired - no action taken'
WHERE status = 'pending_approval' 
AND created_at < NOW() - INTERVAL '30 days';
```

**Rule:** Never DELETE from approval_queue. Void only. The history is the audit trail.

---

## 24.9 Approval Queue Processing Guidelines

**Buck's morning approval workflow (5-10 minutes):**
1. Check ntfy for overnight alerts
2. Open Gateway Owner Console: `GET /gateway/role/owner`
3. Review pending approval count
4. Handle highest-priority items first (bid awards > HubSpot writes > file uploads)
5. Reject with clear reason if unclear — the AI will regenerate or clarify

**Batch approval note:** For large batches (e.g., 40 similar bid import items), Buck can approve categories:
- "Approve all bid imports under $50K" → Claude Code runs a targeted UPDATE
- "Reject all HubSpot writes from today's batch, will review Friday"

This is Buck's decision — Claude Code only executes it, never decides on Buck's behalf.

---

*Cross-reference: Chapter 18 (Monitoring), Chapter 21 (Integrations), Chapter 26 (Emergency)*
