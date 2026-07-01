# Chapter 14 — Financial Management & Approvals
**HCI AI Operations Manual | Part I — Business Operations**
*Authority: Buck Adams | Last Updated: 2026-07-01*

---

## 14.1 Overview

Chapter 08 covers budget structure and controls at the project level. This chapter covers the company-wide financial picture — the accounting console, the approval loop for money moving anywhere in the system, and how historical cost data keeps new estimates honest.

The rule underneath all of it: **nothing that commits company money moves without Buck's approval**, no matter how confident the AI is in the number.

---

## 14.2 The Accounting Console

```
GET /gateway/role/accounting
```

This is the company-wide financial dashboard — the AI equivalent of the accounting department's morning report. It shows, per active project:
- Contract value
- Amount awarded (committed via signed subcontracts)
- Amount in pending bids (not yet awarded)
- Bid package coverage (packages total vs. packages awarded)

And company-wide totals: total contract value across all live projects, total awarded, total pending, commitment percentage, and remaining budget headroom.

**Who uses this:** Buck and anyone doing the books. Whoever reconciles HCI's finances should start here every morning, the same way a PM starts at their project's action list.

---

## 14.3 Pending Financial Approvals

The accounting console also surfaces every pending approval-queue item that has a dollar amount attached, grouped by action type (bid award, change order, purchase order, etc.) with the total dollar value sitting in each bucket:

```
"pending_financial_approvals": [
  {"action_type": "bid_award", "cnt": 3, "total": 842000.00},
  {"action_type": "change_order", "cnt": 1, "total": 12400.00}
]
```

If this number is large or growing, that's a sign approvals are backing up somewhere — check `GET /gateway/approvals/pending` for the specific items and who's sitting on them.

---

## 14.4 The Financial Approval Loop

**Every financial commitment follows the same shape**, regardless of size:

1. **Proposal** — AI or a human proposes an action with a dollar figure (bid award, change order, purchase order, back charge).
2. **Queue** — it lands in `approval_queue` with `status = 'pending'`, the dollar amount in `proposed_payload->>'amount'`, and a priority.
3. **Notification** — Buck is notified via Telegram/ntfy (durable — see Chapter 24) if it crosses a threshold or is time-sensitive.
4. **Decision** — Buck approves, rejects, or holds. Nothing executes on `pending`.
5. **Execution** — only after approval does the system record the commitment (bid marked `awarded`, budget updated, contract prepared).

```
GET  /gateway/approvals/pending
POST /gateway/approvals/{item_id}/approve
POST /gateway/approvals/{item_id}/reject
```

**No AI agent — Claude Code, GBT, or Browser Claude — can move this from proposal to execution on its own.** That gate exists specifically so a confident-sounding recommendation never becomes an actual financial commitment without a human looking at it.

---

## 14.5 Budget vs. Committed Reporting

Two numbers matter for every project, and they are not the same thing:

- **Contract value** — what HCI is being paid for the whole job.
- **Committed** — the sum of everything actually awarded to subs so far (`bid_entries` where `status = 'awarded'`).

The gap between them is what's left to award. When committed approaches contract value with major packages still unawarded, that's a budget exposure — see Chapter 08 §8.3 for a real example (246GW).

```
GET /gateway/project/{code}/budget
```
returns this breakdown per project — contract value, committed, remaining, and percent committed.

---

## 14.6 Historical Cost Data Informing New Estimates

HCI's historical cost record (currently seeded from 655 South Garmisch, 21 records) feeds ROM (Rough Order of Magnitude) estimates for new work:

```
GET /gateway/knowledge/market-rates?division={csi_division}&months_back=24
GET /gateway/knowledge/rom-estimate?sf={square_footage}&...
```

When a new project is scoped or a change order is being priced, check whether a comparable historical cost exists before accepting a sub's number at face value. A price that's wildly out of line with historical data for the same CSI division and market is worth a second look before it goes to Buck for approval.

---

## 14.7 Financial Authority Matrix (Summary)

See Chapter 08 §8.9 for the full authority matrix. The short version: Buck approves every dollar figure that commits company money externally (awards, change orders, purchase orders over routine thresholds). AI agents can draft, analyze, and recommend, but the approval_queue gate is universal — there is no dollar amount small enough to skip it for a first-time vendor or scope change.

**What NOT to do:**
- Do not treat a "pending" approval-queue item as authorized just because the AI proposed it with high confidence.
- Do not let pending financial approvals sit past their `expires_at` window without escalating — check `GET /gateway/executive/mission-control` for `pending_approvals.expiring_soon`.

---

*Next: Chapter 15 — RFI Management*
