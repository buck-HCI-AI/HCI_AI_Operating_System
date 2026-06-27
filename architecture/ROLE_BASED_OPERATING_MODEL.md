# Role-Based Operating Model — HCI AI Construction Intelligence Platform
*BTW-2 | Updated: 2026-06-27*

## Roles and Their Consoles

### Superintendent (SS)
**Daily workflow:** Open SS Console before crew arrives (06:00 push from AUTO-SS-MORNING).

| Need | Where | Endpoint |
|------|-------|----------|
| Today's schedule | SS Console | `/superintendent/{id}` |
| Safety topic | SS Console | Embedded in `/superintendent/{id}/today` |
| Tasks assigned to me | SS Console | `tasks` section |
| Open RFIs | SS Console | `rfis` section |
| Pending decisions | SS Console | `open_decisions` section |
| Procurement status | SS Console | `procurement` section |

**SS Console cadence:** Daily, delivered at 06:00 via ntfy push. Zero login required.

---

### Project Manager (PM)
**Weekly workflow:** Open PM Console Monday morning (07:00 push from AUTO-PM-WEEKLY).

| Need | Where | Endpoint |
|------|-------|----------|
| Budget vs actual | PM Console | `/pm/{id}/weekly` → `budget` |
| Unsigned change orders | PM Console | `change_orders` section |
| Overdue submittals | PM Console | `submittals` section |
| RFI backlog | PM Console | `rfis` section |
| Procurement gaps | PM Console | `procurement` section |
| This week's priorities | PM Console | `next_week_priorities` |
| Full intelligence view | Project Brain | `/services/project-brain/{id}/intelligence` |
| Risk predictions | Predictive Engine | `/services/predictive-engine/{id}/predictions` |

**PM cadence:** Weekly Monday briefing + live endpoint access anytime.

---

### Leadership / Owner (Buck)
**Daily workflow:** Check Executive Dashboard (mobile) and Mission Control.

| Need | Where | Endpoint |
|------|-------|----------|
| Company health | Mission Control | `/executive/mission-control` |
| Pending approvals | Executive Inbox | `/executive/morning-brief` |
| Cross-project risks | Company Snapshot | `/services/cross-project/company-snapshot` |
| What needs me today | Leadership Dashboard | `/leadership/dashboard` |
| AI mission status | Mission Control | `ai_missions` section |
| Weekly company report | Auto-delivered | Friday 16:30 via ntfy |

**Leadership cadence:** Morning brief on wake-up + Friday company report.

---

## 60-Second Company Health Check (Leadership Protocol)

1. Open `/executive/` on phone → see company_health color
2. Scroll to `what_needs_me` → take action on top 1-2 items
3. Check `critical_alerts` → any RED projects?
4. Review `pending_approvals` → approve/reject in-app

Total: under 60 seconds. No spreadsheets. No meetings required.

---

## 5-Minute Full Project Review (Leadership Protocol)

For each of 4 projects (64EW, 101F, 1355R, 83SB):
1. Open `/services/predictive-engine/{id}/predictions` → see all 7 risk areas
2. Check highest-confidence HIGH risks → send to relevant PM/SS
3. Review `/services/project-brain/{id}/risks` → any critical path issues?

Total: ~5 minutes for all 4 projects from phone browser.

---

## Data Flow

```
External Sources → Connectors → PostgreSQL → Intelligence Services → Role Consoles
                                              ↓
                                        Predictions
                                              ↓
                                       ntfy Push Alerts
```

## Automation Calendar

| Time | Workflow | Recipients |
|------|----------|-----------|
| Mon-Fri 06:00 | AUTO-SS-MORNING | Superintendents |
| Monday 07:00 | AUTO-PM-WEEKLY | Project Managers |
| Friday 16:00 | AUTO-WEEKLY-JOB | Leadership |
| Friday 16:30 | AUTO-WEEKLY-COMPANY | Leadership |
| Nightly (planned) | AUTO-SYSTEM-AUDIT | System → executive inbox |
