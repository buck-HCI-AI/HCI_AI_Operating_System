# Volume IV — Superintendent Intelligence
*HCI AI Construction Operating System Architecture Handbook*

---

## 4.1 Superintendent Role Definition (⚠️ Chief Architect Input Required)

*[Chief Architect: Define the superintendent's role in Hendrickson Construction operations,
what information is critical to their daily success, and how AI should support (not replace) their judgment.]*

---

## 4.2 Daily Console — Current Implementation (✅ Live)

**API**: `GET /api/v1/superintendent/{project_id}/today`
**Mobile**: `GET /superintendent/{project_id}` (dark theme, no auth)
**Push**: n8n `AUTO-SS-MORNING` — Mon-Fri 06:00, delivered via ntfy

### Console Sections

```
┌─────────────────────────────────────────┐
│  HCI SS CONSOLE — {PROJECT}             │
│  {DAY}, {DATE}                          │
│  Health: ● {GREEN/YELLOW/RED}           │
├─────────────────────────────────────────┤
│  SAFETY TOPIC TODAY                     │
│  {Rotating toolbox topic}               │
├─────────────────────────────────────────┤
│  SCHEDULE — Activities This Week        │
│  {Items from houzz_schedule_items}      │
├─────────────────────────────────────────┤
│  TASKS — Assigned to This Project       │
│  {Open tasks from houzz_tasks}          │
├─────────────────────────────────────────┤
│  OPEN DECISIONS — Needs Your Input      │
│  {Pending items from executive_inbox}   │
├─────────────────────────────────────────┤
│  PROCUREMENT SNAPSHOT                   │
│  {Open packages, bids out}              │
├─────────────────────────────────────────┤
│  RFIS OPEN                              │
│  {Open RFIs, days outstanding}          │
├─────────────────────────────────────────┤
│  SUBMITTALS PENDING                     │
│  {Pending submittals, deadlines}        │
└─────────────────────────────────────────┘
```

### Safety Topic Rotation (✅ Implemented)

10 topics rotating by weekday:
1. Fall Protection
2. Electrical Safety + Lockout/Tagout
3. Tool Safety + PPE
4. Excavation + Trenching
5. Fire Prevention + Hot Work
6. Hazard Communication (GHS/SDS)
7. Scaffolding + Ladder Safety
8. Silica Dust + Respiratory Protection
9. Heat Illness Prevention
10. Housekeeping + Slip/Trip Prevention

---

## 4.3 Superintendent Weekly Workflow (⚠️ Chief Architect + Buck Input Required)

*[Chief Architect: Define the complete weekly operational cycle for a superintendent at Hendrickson Construction.
What decisions does the SS make each day? What does the SS own vs what they escalate?]*

---

## 4.4 Required Information Model

*[Chief Architect: For every decision a superintendent makes, document what information they need.
The system should proactively surface this information before the SS needs to ask.]*

### Currently Surfaced (✅)

| Information | Source Table | Endpoint Section |
|-------------|-------------|-----------------|
| Schedule activities this week | houzz_schedule_items | `schedule` |
| Open tasks assigned to project | houzz_tasks | `tasks` |
| Pending decisions needing input | executive_inbox | `open_decisions` |
| Open bid packages | bid_packages | `procurement` |
| Open RFIs | rfis | `rfis` |
| Pending submittals | submittals | `submittals` |
| Safety topic | Computed (rotation) | `safety` |
| Project health | Computed | `health` |

### Not Yet Surfaced (⚠️ Future)

- Daily weather forecast integration
- Crew schedule and headcount
- Delivery schedule / materials arriving today
- Punch list items by trade
- Photos / daily log entries
- Subcontractor manpower reports

---

## 4.5 Mobile Experience (✅ Implemented)

**URL**: `http://localhost:8000/superintendent/{id}` (also accessible via ngrok)
- Dark theme (safe for outdoor/bright sun use)
- No login required (internal network)
- Auto-refresh: manual (tap to reload)
- Delivery: ntfy push at 06:00 Mon-Fri links directly to this URL

---

*Ref: [architecture/SUPERINTENDENT_DAILY_CONSOLE_SPEC.md](../architecture/SUPERINTENDENT_DAILY_CONSOLE_SPEC.md)*
