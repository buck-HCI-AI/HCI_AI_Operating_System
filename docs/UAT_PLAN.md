# HCI AI — User Acceptance Testing Plan
**Version:** 1.0 | **Date:** 2026-06-25 | **Directive:** HCI_AI_QA_Testing_and_No_Go_Live_Master_Directive_v1.0  
**Gate:** Gate 4 — requires Gates 1-3 complete first

---

## Purpose

UAT confirms that the system produces output that is correct, useful, and appropriate for Buck's actual construction management work. Technical correctness (Gates 1-3) is necessary but not sufficient — outputs must make sense to Buck reviewing real project data.

---

## Entry Criteria (Gates 1-3 must be complete)

- [x] Gate 1 Engineering Validation: ✅ PASSED 2026-06-25 (see `docs/TEST_RESULTS.md`)
- [x] Gate 2 Integration Testing: ✅ PASSED 2026-06-25 (see `docs/TEST_RESULTS.md`)
- [x] Gate 3 Workflow Acceptance: ✅ PASSED 2026-06-25 (see `docs/WORKFLOW_TEST_MATRIX.md`)
- [x] No P0 or P1 defects open in `docs/KNOWN_ISSUES.md` — confirmed 2026-06-25

**Gate 4 is now OPEN. Buck can run UAT scenarios below.**

---

## UAT Tester

**Buck Adams** — PM & Superintendent, Hendrickson Construction, Inc.; Owner, HCI-AI  
Buck evaluates outputs based on whether they would genuinely replace or improve his current process of managing 4 active projects.

---

## Evaluation Criteria

For each scenario, Buck rates the output:
- **PASS** — Output is correct, useful, and would work in real job situations
- **FAIL** — Output is wrong, confusing, incomplete, or not useful even if technically correct
- **FEEDBACK** — Output is close but needs adjustment (creates a P2 defect, not a blocker)

---

## Tier 1 — Required for Go-Live (5 scenarios)

### UAT-01: Submit a Real Daily Field Log

**Workflow:** WF-SUPER  
**Project:** 101 Francis or 64 Eastwood (Buck's choice — real active project)  
**What to do:**

1. Open Terminal (or .command file on Desktop if available)
2. Submit a real daily log for actual work happening today or yesterday:
```bash
curl -X POST http://localhost:8000/api/v1/workflows/wf-super/daily-log \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{
    "project_number": "101-FRANCIS",
    "work_performed": "[real description of work]",
    "manpower": [actual crew count],
    "weather": "[actual weather]",
    "safety_notes": "[any safety notes, or none]",
    "work_performed_detail": "[more detail]"
  }'
```

**What to evaluate:**
- Does the response make sense?
- Did you receive a field report email at buck@ahmaspen.com?
- Is the email readable and correct — would you actually send this to an owner?
- Does the Project Brain Q&A know about this log afterward?

**UAT-01 Result:** ⬜ PASS / FAIL / FEEDBACK  
**Buck's notes:** _______________

---

### UAT-02: Ask Project Brain a Real Question

**Workflow:** project-brain  
**What to do:** Ask a real question you would actually want answered:
```bash
curl -s -X POST http://localhost:8000/api/v1/services/project-brain/1355-RIVERSIDE/query \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{"question": "[your real question about the project]"}'
```

Example questions:
- "What trades are still missing bids for 1355 Riverside?"
- "What are the open risks on 64 Eastwood?"
- "What is the overall bid coverage for 101 Francis?"

**What to evaluate:**
- Is the answer correct? Does it match what you know about the project?
- Does it cite real data (bid packages, vendor names, risk flags)?
- Would this answer save you time vs. looking it up manually?

**UAT-02 Result:** ⬜ PASS / FAIL / FEEDBACK  
**Buck's notes:** _______________

---

### UAT-03: Review the Morning Brief

**Workflow:** WF-003  
**What to do:** Trigger the morning brief (preview or live):
```bash
curl -s -X POST http://localhost:8000/api/v1/workflows/wf003/morning-brief \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{"preview": false}'
```
Or wait for it to run automatically at 7 AM and check email.

**What to evaluate:**
- Is the email readable and useful?
- Does it cover all 4 projects?
- Could you read it in under 2 minutes and know what needs attention today?
- Are there any factually wrong items?

**UAT-03 Result:** ⬜ PASS / FAIL / FEEDBACK  
**Buck's notes:** _______________

---

### UAT-04: Review the Executive Health Report

**Workflow:** WF-REPORT-EXEC  
**What to do:**
```bash
curl -s -X POST http://localhost:8000/api/v1/workflows/wf-report/exec-health \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{}' > /tmp/exec_health.html && open /tmp/exec_health.html
```

**What to evaluate:**
- Do the health badges (green/yellow/red) reflect actual project reality?
- Is bid coverage % accurate?
- Are risk flags correct?
- Would you share this with your banker or bonding company?

**UAT-04 Result:** ⬜ PASS / FAIL / FEEDBACK  
**Buck's notes:** _______________

---

### UAT-05: Submit a Real Meeting Note

**Workflow:** WF-002  
**What to do:**
```bash
curl -s -X POST http://localhost:8000/api/v1/workflows/wf002/meeting \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 2,
    "title": "[meeting title, e.g. Weekly OAC — 101 Francis]",
    "notes": "[real meeting notes from a recent site meeting]",
    "attendees": ["Buck Adams"],
    "send_email": false
  }'
```
Note: `project_id` values — 64 Eastwood=1, 101 Francis=2, 1355 Riverside=3, 83 Sagebrusch=4

**What to evaluate:**
- Did the meeting save correctly?
- Can you find it later in Project Brain Q&A?
- Are action items captured in a useful way?

**UAT-05 Result:** ⬜ PASS / FAIL / FEEDBACK  
**Buck's notes:** _______________

---

## Tier 2 — Required Before Full Rollout (5 additional scenarios)

### UAT-06: Bid Email Detection

After a real bid email arrives in your Outlook inbox, trigger WF-006:
```bash
curl -s -X POST http://localhost:8000/api/v1/workflows/wf006/inbox-review \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" -d '{}'
```
**Evaluate:** Was the bid detected? Is the amount correct in bid_entries?

**UAT-06 Result:** ⬜ PASS / FAIL / FEEDBACK

---

### UAT-07: PM Daily Review

```bash
curl -s -X POST http://localhost:8000/api/v1/workflows/wf-pm/daily-review/101-FRANCIS \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" -d '{}'
```
**Evaluate:** Is the 5-minute daily check summary useful? Would it replace your current process?

**UAT-07 Result:** ⬜ PASS / FAIL / FEEDBACK

---

### UAT-08: Drive Sync + Brain Reference

After drive sync, ask Project Brain about a specific document that exists in Drive.  
**Evaluate:** Does Brain cite the document? Is the content referenced accurately?

**UAT-08 Result:** ⬜ PASS / FAIL / FEEDBACK

---

### UAT-09: Risk Intelligence

```bash
curl -s http://localhost:8000/api/v1/services/risk-intelligence/flags/64-EASTWOOD \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"
```
**Evaluate:** Are the risk flags real? Are there false positives? Are real risks missing?

**UAT-09 Result:** ⬜ PASS / FAIL / FEEDBACK

---

### UAT-10: Weekly PM Report

```bash
curl -s -X POST http://localhost:8000/api/v1/workflows/wf-report/weekly-pm \
  -H "X-API-Key: hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6" \
  -H "Content-Type: application/json" -d '{}'
```
**Evaluate:** Is this comprehensive enough to replace a manual status meeting?

**UAT-10 Result:** ⬜ PASS / FAIL / FEEDBACK

---

## Exit Criteria

**Tier 1 UAT PASSED when:**
- All 5 Tier 1 scenarios marked PASS or FEEDBACK (no FAILs)
- All FEEDBACK items logged in KNOWN_ISSUES.md as P2 or P3
- Buck verbally confirms: "I'm satisfied with Tier 1"

**Full UAT PASSED when:**
- All 10 scenarios have results
- No FAIL on any Tier 1 scenario
- No FAIL on more than 2 Tier 2 scenarios
- Buck explicitly approves UAT completion in `docs/UAT_RESULTS.md`

---

## Scheduling

UAT can be run in 1-2 business days after Gates 1-3 are confirmed. Scenarios can be run in any order. Tier 1 must be complete before Tier 2.

**Recommended sequence:** UAT-03 (morning brief) → UAT-01 (daily log) → UAT-02 (brain Q&A) → UAT-04 (exec health) → UAT-05 (meeting)
