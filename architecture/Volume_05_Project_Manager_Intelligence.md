# Volume V — Project Manager Intelligence
*HCI AI Construction Operating System Architecture Handbook*

---

## 5.1 PM Role Definition (⚠️ Chief Architect Input Required)

*[Chief Architect: Define the PM's role, what they own, what they escalate, and how AI should
amplify their effectiveness without replacing their judgment.]*

---

## 5.2 PM Weekly Console — Current Implementation (✅ Live)

**API**: `GET /api/v1/pm/{project_id}/weekly`
**Mobile**: `GET /pm/{project_id}` (dark theme, no auth)
**Push**: n8n `AUTO-PM-WEEKLY` — Monday 07:00, delivered via ntfy

### Console Sections

```
┌──────────────────────────────────────────────┐
│  HCI PM WEEKLY — {PROJECT}                   │
│  Week of {DATE}                              │
│  Health: ● {GREEN/YELLOW/RED}                │
├──────────────────────────────────────────────┤
│  BUDGET SNAPSHOT                             │
│  Budget / Actual / Committed / Exposure      │
├──────────────────────────────────────────────┤
│  CHANGE ORDERS — Unsigned                    │
│  {CO count + $ value awaiting approval}      │
├──────────────────────────────────────────────┤
│  PROCUREMENT                                 │
│  Total packages / Awarded / Open / Bids out  │
├──────────────────────────────────────────────┤
│  RFIS — Open + Overdue                       │
│  {RFI count, days outstanding}               │
├──────────────────────────────────────────────┤
│  SUBMITTALS — Pending Approval               │
│  {Count + deadlines}                         │
├──────────────────────────────────────────────┤
│  OPEN DECISIONS                              │
│  {Items from executive_inbox}               │
├──────────────────────────────────────────────┤
│  THIS WEEK'S PRIORITIES                      │
│  {Auto-generated top 5 from data signals}   │
└──────────────────────────────────────────────┘
```

### Priority Generation Algorithm (✅ Implemented)

Auto-generated from highest-severity open signals:
1. Unsigned change orders > $25K
2. Overdue submittals (past required_approval_date)
3. Stale RFIs (> 14 days without response)
4. Open decisions in executive_inbox
5. Open bid packages with no bids received

---

## 5.3 PM Full Intelligence View

### Available (✅)

| Need | Endpoint |
|------|----------|
| Project health | `/api/v1/services/project-brain/{id}/health` |
| All risks | `/api/v1/services/project-brain/{id}/risks` |
| AI narrative | `/api/v1/services/project-brain/{id}/summary` |
| Predictive risks | `/api/v1/services/predictive-engine/{id}/predictions` |
| Schedule risk | `/api/v1/services/predictive-engine/{id}/predictions/schedule` |
| Budget risk | `/api/v1/services/predictive-engine/{id}/predictions/budget` |
| Procurement risk | `/api/v1/services/predictive-engine/{id}/predictions/procurement` |

---

## 5.4 PM Weekly Workflow (⚠️ Chief Architect + Buck Input Required)

*[Chief Architect: Define the complete PM weekly cycle at Hendrickson Construction.
What does the PM review? What decisions do they make? What do they report up?]*

---

## 5.5 PM Decisions Model

*[Chief Architect: List the key decisions a PM makes — change orders, vendor awards, RFI responses,
submittal approvals — and define how AI should support each one.]*

### Currently Supported (✅)

| Decision | AI Support |
|----------|-----------|
| Change order approval | Approval queue + executive_inbox with $ impact |
| Vendor award | Bid leveling service + bid intelligence |
| RFI response | executive_inbox routing |
| Submittal review | submittals table with deadline tracking |

---

## 5.6 PM Reports

| Report | Cadence | Endpoint/Delivery |
|--------|---------|------------------|
| Weekly PM Console | Monday 07:00 | ntfy push + `/pm/{id}` |
| Weekly Job Report | Friday 16:00 | ntfy + `/api/v1/reports/weekly/jobs` |
| Full Intelligence View | On demand | `/api/v1/services/project-brain/{id}/intelligence` |
| Predictive Risks | On demand | `/api/v1/services/predictive-engine/{id}/predictions` |

---

*Ref: [architecture/PM_WEEKLY_CONSOLE_SPEC.md](../architecture/PM_WEEKLY_CONSOLE_SPEC.md)*
