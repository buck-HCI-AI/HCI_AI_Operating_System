# Houzz Browser Agent Strategy
## HCI AI Operating System — Houzz Browser Intelligence Workstream
**Version:** 1.0 | **Created:** 2026-06-26 | **Authority:** HCI_AI_CONSTITUTION.md + AI_TEAM_CHARTER.md  
**Agent:** Browser Claude (GitHub Administrator expanded role for field intelligence)  
**Mode:** Read-Only — No API assumed — Browser navigation only

---

## Strategic Intent

Houzz is Hendrickson Construction's field execution truth — the system where actual project reality is recorded by superintendents every day. The Houzz Browser Intelligence Layer converts that daily field data into executive-grade intelligence without changing a single superintendent behavior.

**The strategy has three pillars:**
1. **Non-invasive:** Houzz is never modified. Superintendents use it exactly as they do today.
2. **Intelligence amplification:** Raw field data becomes structured, actionable intelligence for PMs and executives.
3. **Downstream fuel:** Houzz data feeds HubSpot project health, Drive documentation, and the HCI AI executive dashboard.

---

## Why Browser Agent (Not API)

Houzz Pro does not provide a reliable, documented public API for the data categories HCI AI needs. Browser-based extraction is the correct architectural choice because:

1. **All data is visible in the web UI** — logs, photos, schedule, messages, labor
2. **Browser Claude can read any page** that a human can read
3. **No dependency on Houzz API roadmap** — the intelligence layer is portable
4. **Session-based access** works with existing Houzz authentication
5. **Future-proof:** If Houzz adds an API, the extraction layer can be upgraded without redesigning downstream intelligence

---

## Browser Agent Operating Model

### Agent Identity
- **Agent:** Browser Claude
- **Role expansion:** Read-only intelligence extraction from field execution platform
- **Authority level:** Administrative (per AI_TEAM_CHARTER.md)
- **Session model:** Human-initiated Houzz session; agent reads within active session

### Operating Boundaries
| Permitted | Prohibited |
|---|---|
| Navigate to any Houzz project page | Click edit, save, submit on any form |
| Read all text, data, and captions | Send messages to clients or contacts |
| View and note photo metadata | Upload, delete, or annotate photos |
| Read schedule activities and status | Modify schedule, dates, or tasks |
| Read labor entries | Create or modify labor records |
| Read budget summaries | Enter or approve financial data |
| Read selections status | Make or approve selections |
| Extract data to structured format | Write extracted data back to Houzz |

---

## Extraction Architecture

### Layer 1 — Navigation
Browser Claude navigates Houzz's standard web interface using predictable URL and UI patterns. Navigation paths are documented in HOUZZ_READ_ONLY_AUDIT.md.

### Layer 2 — Structured Extraction
Raw Houzz page content is read and converted to HCI AI's standard data schema:

```
HCI Houzz Data Schema v1.0
{
  "extraction_date": "YYYY-MM-DD",
  "extraction_time": "HH:MM",
  "project": {
    "name": "",
    "houzz_id": "",
    "status": ""
  },
  "daily_log": {
    "date": "",
    "submitted_by": "",
    "submitted_at": "",
    "narrative": "",
    "weather": {
      "conditions": "",
      "temp_high": "",
      "temp_low": "",
      "precipitation": "",
      "work_impact": ""
    },
    "labor": [
      {"name": "", "trade": "", "hours": 0, "area": ""}
    ],
    "subcontractors": [
      {"company": "", "trade": "", "headcount": 0, "area": ""}
    ],
    "materials_received": [
      {"item": "", "quantity": "", "vendor": "", "po_ref": ""}
    ],
    "equipment": [],
    "safety": {"incidents": false, "observations": ""},
    "open_issues": [],
    "photos": {"count": 0, "captions": []}
  },
  "schedule": {
    "activities_in_progress": [],
    "activities_completed_today": [],
    "activities_planned_not_started": [],
    "activities_ahead": [],
    "activities_behind": []
  },
  "extraction_metadata": {
    "agent": "Browser Claude",
    "session_id": "",
    "pages_read": [],
    "errors": []
  }
}
```

### Layer 3 — Intelligence Analysis (ChatGPT)
Structured extraction data is passed to ChatGPT for:
- Pattern recognition (recurring issues, productivity trends)
- Risk classification (schedule, safety, quality, procurement)
- Narrative generation (executive summary, PM action items)
- Anomaly detection (unusual labor counts, missing subs, weather impacts)

### Layer 4 — Output Routing (n8n)
Processed intelligence is routed to:
- Repository (committed as structured report)
- PM notification channel (internal)
- HubSpot project health field (pending Gate H approval)
- Executive dashboard (read from repository)

---

## Multi-Project Strategy

For companies with multiple active projects, the Browser Agent operates sequentially:

1. Load project list from HCI AI project registry
2. For each active project (status: Construction):
   a. Navigate to Houzz project
   b. Extract daily log
   c. Extract schedule snapshot
   d. Extract photo count and recent captions
   e. Save structured extraction
3. Run ChatGPT intelligence generation per project
4. Compile cross-project executive summary (portfolio view)
5. Flag any project in Red status for immediate PM alert

**Estimated extraction time per project:** 3–5 minutes  
**Maximum projects per daily run:** 10 (expand with parallel sessions in future sprints)

---

## Photo Intelligence Strategy

Photos are a critical but underutilized Houzz data source. The strategy:

**Phase 1 (Sprint 3) — Metadata extraction:**
- Count of photos taken today
- Photo captions as extracted text
- Photo timestamps
- Work area association (from caption or log context)

**Phase 2 (Sprint 5) — Visual intelligence:**
- Browser Claude navigates to full-size photo view
- Vision AI analyzes photo content for:
  - Work area depicted
  - Progress stage (rough, finish, etc.)
  - Safety compliance indicators
  - Quality concern flags
  - Before/after comparison potential

**Phase 3 (Sprint 7) — Photo-to-report integration:**
- Selected photos automatically attached to executive summary
- Photo evidence linked to schedule milestone completion
- Photo archive indexed for historical project mining

---

## Schedule Intelligence Strategy

Houzz schedule data provides the ground truth for:

| Signal | HCI AI Use |
|---|---|
| Activities completed today | Schedule performance tracking |
| Activities behind plan | Risk alert generation |
| Schedule float consumed | Milestone risk assessment |
| Sub mobilization vs. plan | Sub performance tracking |
| Critical path activity status | Executive dashboard signal |

**Extraction approach:**
1. Read Houzz schedule view (Gantt or list)
2. Capture each activity: name, planned dates, actual dates, status, % complete
3. Compare against baseline (stored in Drive or repository)
4. Calculate variance: days ahead/behind per activity
5. Identify critical path activities at risk

---

## Superintendent Intelligence Assistant Strategy

Beyond reading completed logs, the Browser Intelligence Layer supports superintendents with a **Draft Assistant** (separate from read-only extraction):

**How it works:**
1. Superintendent opens Houzz daily log form
2. Before they start typing, they review a pre-populated draft prepared by HCI AI based on:
   - Yesterday's open issues (carried forward)
   - Schedule activities planned for today
   - Expected material deliveries from procurement log
   - Weather forecast for project location
3. Superintendent edits the draft to reflect actual field conditions
4. Superintendent submits as their own log (no AI submission)

**This is advisory only — superintendent always controls submission.**  
**Gate E applies if any client-visible content is modified by AI suggestion.**

---

## Integration with HCI AI Systems

| Target System | Data Flow | Gate Required |
|---|---|---|
| HubSpot Project Record | Daily health status, schedule variance | Gate H |
| Google Drive | Daily intelligence report filed to project folder | No gate (AI folder write) |
| Executive Dashboard | Portfolio project health signals | No gate (read from repository) |
| GitHub Repository | All reports committed | No gate (standard commit) |
| n8n Workflows | Trigger and routing | No gate (internal) |

---

## Roadmap

| Sprint | Capability |
|---|---|
| Sprint 1 | Manual Browser Claude read + extraction template established |
| Sprint 2 | n8n trigger automation for daily extraction |
| Sprint 3 | ChatGPT intelligence generation automated |
| Sprint 4 | Photo metadata extraction + executive summary delivery |
| Sprint 5 | Schedule intelligence + variance analysis |
| Sprint 6 | Cross-project portfolio view |
| Sprint 7 | Visual photo intelligence (vision AI) |
| Sprint 8 | Superintendent draft assistant |
| Sprint 9 | Full production — daily automated intelligence package |

---

*Governed by HCI_AI_CONSTITUTION.md | Houzz Browser Intelligence Workstream | Hendrickson Construction, Inc.*
