#!/usr/bin/env python3
"""
HCI Command Center — Daily Operating Loop
Queries all live services and generates a single consolidated report for Buck.
Output: reports/daily/YYYY-MM-DD-hci-command-center.md
Triggered: n8n AUTO-001 daily at 07:00, or manually.
Read-only — no writes to external systems.
"""
import json, os, sys, subprocess, urllib.request
from datetime import datetime, timezone, date

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_KEY_FILE = os.path.join(REPO_ROOT, ".env")

sys.path.insert(0, os.path.join(REPO_ROOT, "03_Source_Code", "api"))


# ── Config ────────────────────────────────────────────────────────────────────

def _load_env():
    env = {}
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

_ENV = _load_env()
API_KEY = _ENV.get("HCI_API_KEY", "")
API_BASE = "http://localhost:8000"
N8N_BASE = "http://localhost:5678"
N8N_KEY = _ENV.get("N8N_API_KEY", "")


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def _api_get(path: str, auth: bool = True) -> dict:
    try:
        headers = {"X-API-Key": API_KEY} if auth else {}
        req = urllib.request.Request(f"{API_BASE}{path}", headers=headers)
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def _n8n_get(path: str) -> dict:
    try:
        req = urllib.request.Request(
            f"{N8N_BASE}{path}",
            headers={"X-N8N-API-KEY": N8N_KEY}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}


def _docker_status(container: str) -> str:
    try:
        r = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", container],
            capture_output=True, text=True, timeout=5
        )
        s = r.stdout.strip()
        return "🟢 running" if s == "running" else f"🔴 {s}" if s else "❌ not found"
    except Exception as e:
        return f"❌ {e}"


# ── Data collection ───────────────────────────────────────────────────────────

def collect_service_health():
    health = _api_get("/api/v1/health")
    svcs = health.get("services", {})
    rows = []
    for name, info in svcs.items():
        st = info.get("status", "unknown") if isinstance(info, dict) else str(info)
        icon = "🟢" if st in ("ok", "healthy", "connected") else "🔴"
        rows.append(f"| {name} | {icon} {st} |")

    pg = _docker_status("hci_postgres")
    qdrant = _docker_status("hci_qdrant")
    redis = _docker_status("hci_redis")

    return rows, {"postgres": pg, "qdrant": qdrant, "redis": redis}


def collect_approval_queue():
    data = _api_get("/api/v1/services/approval-queue/pending")
    if "error" in data:
        return [], data["error"]

    items = data if isinstance(data, list) else data.get("items", [])
    top = items[:10]
    rows = []
    for item in top:
        title = (item.get("target_description") or item.get("title") or "—")[:60]
        prio = item.get("priority", "—")
        atype = item.get("action_type", "—")
        rows.append(f"| {title} | {atype} | {prio} |")

    total = len(items)
    return rows, total


def collect_n8n_workflows():
    data = _n8n_get("/api/v1/workflows?limit=50")
    if "error" in data:
        return [], data["error"]

    workflows = data.get("data", [])
    active = [w for w in workflows if w.get("active")]
    inactive = [w for w in workflows if not w.get("active")]

    rows = []
    for w in active[:12]:
        name = w.get("name", "—")[:50]
        rows.append(f"| {name} | 🟢 Active |")
    for w in inactive[:3]:
        name = w.get("name", "—")[:50]
        rows.append(f"| {name} | ⚪ Inactive |")

    return rows, len(active), len(workflows)


def collect_mining_status():
    data = _api_get("/api/v1/services/mining/status")
    return data


def collect_houzz_status():
    data = _api_get("/api/v1/services/houzz/status")
    return data


def collect_projects():
    data = _api_get("/api/v1/projects")
    if "error" in data:
        return []
    items = data if isinstance(data, list) else data.get("projects", [])
    return items


# ── Report generation ─────────────────────────────────────────────────────────

def generate_report() -> str:
    now = datetime.now(timezone.utc)
    today = date.today().isoformat()
    ts = now.strftime("%Y-%m-%d %H:%M UTC")

    health_rows, docker = collect_service_health()
    aq_rows, aq_total = collect_approval_queue()
    wf_rows, wf_active, wf_total = collect_n8n_workflows()
    mining = collect_mining_status()
    houzz = collect_houzz_status()

    # ── Approval queue section ────────────────────────────────────────────────
    aq_count = aq_total if isinstance(aq_total, int) else "?"
    aq_section = ""
    if isinstance(aq_rows, list) and aq_rows:
        aq_section = "| Action | Type | Priority |\n|---|---|---|\n" + "\n".join(aq_rows)
    else:
        aq_section = "_No pending items or service error._"

    # ── n8n section ───────────────────────────────────────────────────────────
    wf_section = ""
    if isinstance(wf_rows, list) and wf_rows:
        wf_section = "| Workflow | Status |\n|---|---|\n" + "\n".join(wf_rows)
    else:
        wf_section = "_Cannot reach n8n or no workflows._"

    # ── Service health section ────────────────────────────────────────────────
    health_section = ""
    if health_rows:
        health_section = "| Service | Status |\n|---|---|\n" + "\n".join(health_rows)
    else:
        health_section = "_FastAPI not responding._"

    # ── Mining status ─────────────────────────────────────────────────────────
    if "error" not in mining:
        miners = mining.get("miners", {})
        mining_rows = "\n".join(
            f"| {name} | {info.get('status','—')} | {info.get('last_run','—')} |"
            for name, info in miners.items()
        ) if miners else "_No miner data._"
    else:
        mining_rows = f"_Mining service error: {mining.get('error')}_"

    # ── Houzz section ─────────────────────────────────────────────────────────
    if "error" not in houzz:
        counts = houzz.get("table_counts", {})
        houzz_section = (
            f"- houzz_projects: **{counts.get('houzz_projects', 0)}** rows\n"
            f"- houzz_daily_logs: **{counts.get('houzz_daily_logs', 0)}** rows\n"
            f"- houzz_schedule_items: **{counts.get('houzz_schedule_items', 0)}** rows"
        )
    else:
        houzz_section = "_Houzz service error._"

    # ── Docker ────────────────────────────────────────────────────────────────
    docker_section = "\n".join(f"- {k}: {v}" for k, v in docker.items())

    report = f"""# HCI Command Center — Daily Report
**{ts}**
**Authority:** Chief Architect Directive — Reduce Buck Inputs (2026-06-27)
**Generated by:** scripts/generate_command_center.py

> **Buck's daily read:** Scan Decisions Needed + Blockers. Everything else is status.

---

## 🚦 Service Health

{health_section}

**Infrastructure (Docker):**
{docker_section}

---

## 📋 Approval Queue — Needs Buck Action

**Total pending: {aq_count}**

{aq_section}

> Full queue: `GET /api/v1/services/approval-queue/pending`

---

## 🔄 n8n Workflows ({wf_active} active of {wf_total} total)

{wf_section}

---

## ⛏ Mining Engine Status

| Miner | Status | Last Run |
|---|---|---|
{mining_rows}

---

## 🏗 Houzz Intelligence

{houzz_section}

> Bridge endpoint live: `POST /api/v1/services/houzz/ingest`
> Browser Claude directive: `BROWSER_CLAUDE_HOUZZ_PERSISTENCE_DIRECTIVE.md` (Desktop)

---

## ⚠️ Blockers

_Populated by agents when they hit a wall. Empty = no blockers._

| Blocker | Raised By | Since |
|---|---|---|
| Browser Claude: 101 Francis Houzz data not yet POSTed to ingestion endpoint | Claude Code | 2026-06-27 |

---

## 🤔 Decisions Needed from Buck

| # | Decision | Default if No Response | Deadline |
|---|---|---|---|
| 1 | Approve 6 vendor registry merges (Ajax x7, 2H Mech x2, AAA Mountain x2, ANB Bank x2, Ajac Stone x2, Ajax Electric x2) | Hold | ASAP |
| 2 | Approve making GitHub repo private (recommended for API key security) | Repo stays public | No deadline |
| 3 | Authorize Browser Claude to POST 101 Francis Houzz data to ingestion endpoint | Pending directive review | After reviewing Desktop directive |

---

## ✅ Recommended Next Actions

**Claude Code:**
1. Monitor Houzz ingestion — trigger HouzzMiner after Browser Claude posts data
2. Vendor registry merge — awaiting Buck approval (item #1 above)

**Browser Claude:**
1. Read `BROWSER_CLAUDE_HOUZZ_PERSISTENCE_DIRECTIVE.md` from Desktop
2. Extract 101 Francis daily logs + schedule items → POST to `/api/v1/services/houzz/ingest`

**ChatGPT (Chief Architect):**
1. Review Sprint 2.5 hardening — approve migration 006 schema extension
2. Issue ACR for Houzz full extraction (15-table scope per HOUZZ_EXTRACTION_BACKLOG.md)

**Buck:**
1. Approve vendor registry merges ↑
2. Review approval queue top items
3. No other coordination needed — agents handle the rest

---

## 📊 Sprint 2 Progress

See `CURRENT_SPRINT.md` for full board.

---

*HCI AI Operating System | Hendrickson Construction, Inc.*
*Report auto-generated — do not edit manually.*
"""

    return report


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    today = date.today().isoformat()
    output_dir = os.path.join(REPO_ROOT, "reports", "daily")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{today}-hci-command-center.md")

    report = generate_report()

    with open(output_path, "w") as f:
        f.write(report)

    print(f"✅ Command center report written to: {output_path}")
    print(report[:500])


if __name__ == "__main__":
    main()
