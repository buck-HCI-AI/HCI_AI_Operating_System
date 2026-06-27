# Volume VI — Executive Mission Control
*HCI AI Construction Operating System Architecture Handbook*

---

## 6.1 Executive Intelligence Philosophy (⚠️ Chief Architect Input Required)

*[Chief Architect: Define how an owner/executive should interact with the platform.
What is the 60-second company health check? What requires executive judgment vs AI autonomy?]*

---

## 6.2 Current Implementation (✅ Live)

### Executive Endpoints

| Endpoint | Description | Use Case |
|----------|-------------|---------|
| `GET /api/v1/executive/mission-control` | Full portfolio intelligence — 11 sections | Morning review |
| `GET /api/v1/executive/morning-brief` | Prioritized inbox + items needing decision | Daily briefing |
| `GET /api/v1/leadership/dashboard` | Sprint 3 summary dashboard | Quick status |
| `GET /api/v1/reports/weekly/company` | Company-wide Friday report | Weekly review |
| `GET /executive/` | Mobile HTML dashboard | Phone access |

### Mission Control Response (✅ 11 Sections)

```json
{
  "company_health": "YELLOW",
  "portfolio": {
    "projects": [...],          // 4 projects with health + risk counts
    "projects_at_risk": 2
  },
  "ai_missions": {
    "counts": {"in_progress": 2, "blocked": 2, "open": 0, "completed": 2},
    "active_missions": [...]
  },
  "ai_productivity": {
    "last_30_days": {
      "total_minutes_saved": 2748,
      "docs_processed": 147,
      "errors_caught": 23,
      "workflow_runs": 891
    },
    "hours_saved": 45.8
  },
  "pending_approvals": {
    "summary": {"total_pending": N, "critical": N, "expiring_soon": N},
    "top_items": [...]
  },
  "critical_alerts": {"count": 3, "alerts": [...]},
  "top_risks": [...],
  "top_opportunities": [...],
  "weekly_trends": [...],
  "kpi_dashboard": [...],
  "procurement_pulse": {"open_packages": 119, "awarded_packages": 0},
  "connector_health": {"connectors": [...], "stale_count": N}
}
```

---

## 6.3 Mobile Dashboard (✅ Live)

**URL**: `http://localhost:8000/executive/` (also via ngrok tunnel)
- Approval action buttons (Approve/Reject/Defer) — mobile tap to action
- Auto-refreshes every 60 seconds
- Dark theme
- Sections: project health · inbox · decisions · AI activity · ROI

---

## 6.4 Approval Workflow (✅ Implemented)

```
AI detects action needed
        │
        ▼
approval_queue (status=pending)
        │
        ▼
executive_inbox (approve/reject/defer tokens)
        │
        ▼
ntfy push notification → Buck taps Approve/Reject/Defer
        │
        ▼
Token URL validates → action executed → status updated
```

**Security**: Each token is single-use, expires after N hours, stored hashed in DB.

---

## 6.5 Sections to be Authored (⚠️ Chief Architect)

### 6.5.1 Portfolio Intelligence Model
*[Chief Architect: How should leadership view the portfolio? What aggregations matter most?]*

### 6.5.2 Decision Dashboard
*[Chief Architect: What decisions require executive review vs PM/SS autonomy?]*

### 6.5.3 Company KPIs
*[Chief Architect: Define the KPIs that matter to Hendrickson Construction leadership]*

### 6.5.4 Risk Heat Maps
*[Chief Architect: How should risk be visualized across the portfolio?]*

### 6.5.5 Strategic Planning Integration
*[Chief Architect: How does the platform support 90-day and annual planning?]*

### 6.5.6 Weekly Executive Review Protocol
*[Chief Architect: Define the structured weekly review process for Buck]*

---

*Ref: [architecture/LEADERSHIP_MISSION_CONTROL_SPEC.md](../architecture/LEADERSHIP_MISSION_CONTROL_SPEC.md)*
