# CYCLE10_GBT_CPM_SCHEDULE_INTELLIGENCE
## Date: 2026-07-01 | Cycle: 10 | Source: GBT Chief Architect

## GBT Summary
"This gives HCI the first real CPM scheduling intelligence layer:
not just schedule dates, but dependency-aware risk detection."

---

## 1. CPM Algorithm — Forward/Backward Pass

### Step 1: Load cpm_activities from DB (project_id)
Build dict: { activity_id -> CpmActivity }

### Step 2: Validate Graph (no cycles)
Return 400 if schedule graph contains cycle.

### Step 3: Topological Sort — Kahn's Algorithm
in_degree = {aid: 0 for aid in activities}
for activity in activities.values():
    for pred in activity.predecessors:
        in_degree[activity.activity_id] += 1
queue = deque of activities where in_degree == 0
Process queue -> ordered list
If len(ordered) != len(activities): raise ValueError("cycle detected")

### Step 4: Forward Pass (Early Start / Early Finish)
For each activity in topological order:
    ES = max(EF of all predecessors) -- for FS relationships
    EF = ES + duration_days
    Project EF = max(EF of all leaf activities)

### Step 5: Backward Pass (Late Start / Late Finish)
For each activity in reverse topological order:
    LF = min(LS of all successors)
    LS = LF - duration_days

### Step 6: Calculate Float + Mark Critical
float_days = LF - EF  (total float)
is_critical = (float_days == 0)

### Step 7: Persist Results to cpm_activities
UPDATE cpm_activities SET float_days=:float, is_critical=:critical
WHERE project_id=:project_id AND activity_id=:activity_id

### Service Function Signature
def calculate_cpm(project_id: str, db: Session) -> dict:
    activities = load_activities(project_id, db)
    validate_graph(activities)
    ordered = topological_sort(activities)
    forward_pass(activities, ordered)
    backward_pass(activities, ordered)
    persist_results(project_id, activities, db)
    return { "critical_path_count": N, "project_ef": date, ... }

Supported relationships for Phase 1:
  FS = Finish-to-Start (implement first)
  SS = Start-to-Start
  FF = Finish-to-Finish
  SF = Start-to-Finish (implement later)

---

## 2. Schedule Variance Detection

### Activity-Level Variance
If end_actual is set: variance_days = (end_actual - end_planned).days
If not complete and today > end_planned: variance_days = (today - end_planned).days
Positive = late. Negative = early.

### Project-Level Variance
critical_path_delay_days = max(variance_days for critical activities)
Also track: delayed_critical, blocked_critical, activities_with_negative_float, missed_milestones

### GREEN Conditions
critical path delay = 0
no critical activities blocked
no milestone missed
float remains available
no procurement/RFI/submittal blockers affect critical path

### YELLOW Triggers (any one = YELLOW)
critical path delay 1-4 days
any milestone missed by 1-4 days
1 critical activity BLOCKED
float < 3 days on critical activity
unresolved RFI blocks critical work for 1-2 days

### RED Triggers (any one = RED)
critical path delay >= 5 days  <-- 101F fix: -5 days = RED
any milestone missed by >= 5 days
2 or more critical activities BLOCKED
critical activity delayed with zero or negative float
schedule completion date slips beyond contractual milestone
unresolved RFI blocks critical work for >= 3 days
long-lead procurement delay impacts critical path

---

## 3. FastAPI Endpoints

### A) POST /schedule/import
Accepts: CSV or XER file (P6 export)
Form fields: project_id (str), format (csv|xer), file (UploadFile)
File size limit: 20MB
Allowed extensions: .csv, .xer

On success:
- Saves file to /tmp/hci_schedule_uploads/
- Background task: parse + load to cpm_activities + calculate_cpm()
- Returns: { status: "PROCESSING", import_id, project_id, activity_count_estimate }

Error handling:
- 400: invalid format, wrong extension, empty file, file too large
- 422: missing project_id or format
- 500: DB failure or parse error

### B) GET /schedule/{project_id}/critical-path
Triggers recalculation if stale (no CPM run in last 24h).
Returns:
{
  "project_id": "101F",
  "critical_path_count": 12,
  "critical_path": [
    {
      "activity_id": "A1010",
      "name": "Steel Erection",
      "duration_days": 5,
      "start_planned": "2026-07-15",
      "end_planned": "2026-07-20",
      "start_actual": "2026-07-15",
      "end_actual": null,
      "float_days": 0,
      "is_critical": true,
      "status": "IN_PROGRESS",
      "trade": "Structural Steel"
    }
  ]
}

### C) GET /schedule/{project_id}/variance-report
Returns health status + variance detail:
{
  "project_id": "101F",
  "status": "RED",
  "critical_path_delay_days": 5,
  "projected_completion_variance_days": 5,
  "summary": "Steel procurement delay is impacting critical path.",
  "triggers": [
    {
      "severity": "RED",
      "type": "CRITICAL_PATH_DELAY",
      "message": "Critical path delay is 5 days"
    }
  ],
  "delayed_critical_activities": [...],
  "blocked_critical_activities": [],
  "missed_milestones": []
}

---

## 4. Claude Code Implementation Checklist

- [ ] Create app/services/cpm_service.py with calculate_cpm()
- [ ] Implement validate_graph() (cycle detection)
- [ ] Implement topological_sort() with Kahn's algorithm
- [ ] Implement forward_pass() (ES/EF calculation)
- [ ] Implement backward_pass() (LS/LF calculation)
- [ ] Implement persist_results() (update float_days, is_critical in DB)
- [ ] Create api/routers/schedule.py with 3 endpoints
- [ ] Build CSV parser for schedule import
- [ ] Build XER parser stub (Phase 2 full XER parsing)
- [ ] Wire schedule router into main.py
- [ ] Test: valid CSV import -> activities in DB
- [ ] Test: invalid file type -> 400
- [ ] Test: circular dependency -> 400
- [ ] Test: critical path calculation correct
- [ ] Test: 101F with -5 day delay -> RED status
- [ ] Test: yellow trigger (1-4 day delay)
- [ ] Test: red trigger (>= 5 day delay)
- [ ] Test: blocked critical activity trigger
- [ ] Commit: feat: CPM scheduling intelligence - schedule import + critical path + variance

---

## 5. 101F Fix Confirmation

The CPM variance report directly resolves the 101F schedule variance bug:
- Previous state: executive report showed variance = 1 (incorrect)
- Root cause: no CPM engine, variance manually entered incorrectly
- Fix: Once schedule imported, CPM engine calculates -5 days automatically
- Result: GET /schedule/101F/variance-report returns status=RED, delay=-5 days
- Executive report and Mission Control will reflect canonical CPM-calculated value

---

## Cycle 10 Status: COMPLETE
Next: Fire GBT Cycle 11 for Cost Forecasting intelligence architecture.
