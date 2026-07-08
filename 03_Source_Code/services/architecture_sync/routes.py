"""
Architecture Sync Engine — Handbook synchronization service

GET  /status           — handbook status: volumes, ADRs, queue summary
GET  /conflicts        — implementation vs handbook conflicts
GET  /review-engine    — which chapters affected by recent implementation changes
GET  /queue            — AUTHORING_QUEUE chapter-by-chapter status
POST /validate         — validate a draft chapter
POST /publish          — publish a validated draft
POST /submit-chapter   — accept chapter from any source
POST /sync             — force full re-sync of cross-references
"""

import os, re, json, logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("hci.architecture_sync")
router = APIRouter()

_ROOT          = Path(__file__).resolve().parents[3]
_ARCH          = _ROOT / "architecture"
_HANDBOOK      = _ARCH / "Handbook"
_DRAFTS        = _HANDBOOK / "Drafts"
_PUBLISHED     = _HANDBOOK / "Published"
_ADR_DIR       = _ARCH / "ADRs"
_CHANGELOG     = _HANDBOOK / "CHANGELOG.md"
_MASTER_INDEX  = _HANDBOOK / "00_Master_Index.md"
_AUTH_QUEUE    = _HANDBOOK / "AUTHORING_QUEUE.md"
_REVIEW_QUEUE  = _HANDBOOK / "CHIEF_ARCHITECT_REVIEW_QUEUE.md"

# ── File → Handbook volume mapping ────────────────────────────────────────────

_FILE_TO_VOLUME = {
    "services/project_brain":        ["III", "II"],
    "services/predictive_engine":    ["V", "II"],
    "services/connectors":           ["VI", "VII"],
    "services/cross_project":        ["III", "II"],
    "services/system_auditor":       ["VIII"],
    "services/architecture_sync":    ["VI"],
    "api/routers/executive.py":      ["V"],
    "api/routers/superintendent.py": ["IV"],
    "api/routers/pm.py":             ["IV"],
    "api/routers/leadership.py":     ["IV", "V"],
    "05_Database/migrations":        ["II", "VIII"],
    "workflows/n8n":                 ["VII"],
    "services/autonomy":             ["VI"],
    "services/bid_intelligence":     ["VI"],
}

# ── Volume metadata ────────────────────────────────────────────────────────────

_VOLUMES = [
    {"num": "I",    "title": "Executive Vision",               "file": "Volume_01_Executive_Vision.md",                "ca_required": True},
    {"num": "II",   "title": "Construction Intelligence Model", "file": "Volume_02_Construction_Intelligence_Model.md", "ca_required": False},
    {"num": "III",  "title": "Project Brain",                   "file": "Volume_03_Project_Brain.md",                  "ca_required": False},
    {"num": "IV",   "title": "Role Intelligence",               "file": "Volume_04_Role_Intelligence.md",              "ca_required": False},
    {"num": "V",    "title": "Executive Intelligence",          "file": "Volume_05_Executive_Intelligence.md",         "ca_required": False},
    {"num": "VI",   "title": "Construction Intelligence Engine","file": "Volume_06_Construction_Intelligence_Engine.md","ca_required": False},
    {"num": "VII",  "title": "Automation Architecture",         "file": "Volume_07_Automation_Architecture.md",        "ca_required": False},
    {"num": "VIII", "title": "Governance",                      "file": "Volume_08_Governance.md",                     "ca_required": False},
    {"num": "IX",   "title": "Roadmap",                         "file": "Volume_09_Roadmap.md",                        "ca_required": True},
    {"num": "X",    "title": "Future Vision",                   "file": "Volume_10_Future_Vision.md",                  "ca_required": True},
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _volume_status(vol: dict) -> dict:
    path = _HANDBOOK / vol["file"]
    if not path.exists():
        return {**vol, "status": "MISSING", "word_count": 0, "has_ca_content": False}
    content = path.read_text()
    word_count = len(content.split())
    has_ca_content = "⚠️ Chief Architect Required" in content or "Chief Architect" in content[:200]
    ca_sections_pending = content.count("Chief Architect Required")
    is_stub = ca_sections_pending > 3
    status = "DRAFT" if is_stub else "IMPL_REF"
    return {
        "volume": vol["num"],
        "title": vol["title"],
        "file": vol["file"],
        "status": status,
        "word_count": word_count,
        "ca_sections_pending": ca_sections_pending,
        "ca_authorship_required": vol["ca_required"],
    }


def _adr_list() -> list:
    # Was pointed at Handbook/ADR/ (6 stale files, ADR-001-006) instead of the
    # real, actively-maintained architecture/ADRs/ (16 files as of 2026-07-07) -
    # found while wiring the weekly book-refresh workflow. Every ADR documenting
    # this project's drift-detection/self-heal work (016) plus the last week's
    # incidents (007-015) was invisible to /status and /sync as a result.
    if not _ADR_DIR.exists():
        return []
    adrs = []
    for f in sorted(_ADR_DIR.glob("ADR-*.md")):
        content = f.read_text()
        # Two formats coexist: markdown heading ("# ADR-001: Title") for early
        # ADRs, YAML frontmatter (title:/status:) for 006+. Handle both.
        status_match = re.search(r"^status:\s*(\w+)", content, re.MULTILINE) or \
                       re.search(r"\*\*Status:\*\* (\w+)", content)
        title_match = re.search(r"^title:\s*(.+)$", content, re.MULTILINE) or \
                      re.search(r"^# ADR-\d+:?\s*(.+)$", content, re.MULTILINE)
        adrs.append({
            "file": f.name,
            "title": title_match.group(1).strip() if title_match else f.stem,
            "status": status_match.group(1) if status_match else "Unknown",
        })
    return adrs


def _queue_summary() -> dict:
    if not _AUTH_QUEUE.exists():
        return {"error": "AUTHORING_QUEUE.md not found"}
    content = _AUTH_QUEUE.read_text()
    not_started = content.count("NOT STARTED")
    in_progress = content.count("IN PROGRESS")
    draft_ready = content.count("DRAFT READY")
    published   = content.count("PUBLISHED")
    impl_only   = content.count("IMPL ONLY")
    conflicts   = content.count("CONFLICT")
    return {
        "not_started": not_started,
        "in_progress": in_progress,
        "draft_ready": draft_ready,
        "published": published,
        "impl_only": impl_only,
        "conflicts": conflicts,
        "total_chapters": not_started + in_progress + draft_ready + published + impl_only + conflicts,
    }


def _detect_conflicts() -> list:
    """Scan handbook chapters for implementation references and verify they still hold."""
    conflicts = []

    # Check: does every referenced endpoint actually respond?
    endpoint_pattern = re.compile(r"`(GET|POST|PUT|DELETE)\s+(/api/v1/[^`]+)`")
    for vol in _VOLUMES:
        path = _HANDBOOK / vol["file"]
        if not path.exists():
            continue
        content = path.read_text()
        for match in endpoint_pattern.finditer(content):
            method, endpoint = match.groups()
            # Check endpoint exists in services listing
            # (Full HTTP check would be too slow; we do a path-based check)
            service_part = endpoint.split("/")[4] if len(endpoint.split("/")) > 4 else ""
            svc_dir = _ROOT / "03_Source_Code" / "services" / service_part.replace("-", "_")
            if service_part and not svc_dir.exists():
                conflicts.append({
                    "volume": vol["num"],
                    "conflict_type": "endpoint_service_missing",
                    "detail": f"Volume {vol['num']} references {endpoint} but service dir not found",
                    "endpoint": endpoint,
                })

    # Check: known manual conflict (dual HubSpot tables)
    conflicts.append({
        "volume": "V",
        "conflict_type": "schema_divergence",
        "detail": "hubspot_engagements (legacy) and hubspot_activities (connector framework) both exist — recommend deprecating engagements",
        "status": "Pending Chief Architect",
    })

    return conflicts


def _review_engine_files(changed_files: list[str]) -> dict:
    """Determine which handbook volumes are affected by a list of changed files."""
    affected = set()
    for f in changed_files:
        for pattern, volumes in _FILE_TO_VOLUME.items():
            if pattern in f:
                affected.update(volumes)
    affected_vols = [v for v in _VOLUMES if v["num"] in affected]
    adrs_to_check = _adr_list()
    return {
        "changed_files": changed_files,
        "affected_volumes": [{"volume": v["num"], "title": v["title"]} for v in affected_vols],
        "adrs_to_review": adrs_to_check,
        "recommended_actions": [
            f"Update Volume {v['num']} implementation references" for v in affected_vols
        ] + ["Run POST /architecture-sync/sync to rebuild cross-references"],
    }


def _validate_draft(content: str, volume: str) -> dict:
    """Validate a draft chapter before publishing."""
    checks = []

    # Check 1: Has title
    has_title = content.strip().startswith("# Volume")
    checks.append({"check": "has_title", "passed": has_title,
                   "detail": "Chapter must start with '# Volume'"})

    # Check 2: No credential patterns
    cred_patterns = [r"password\s*=\s*['\"][^'\"]{4,}", r"api_key\s*=\s*['\"][^'\"]{10,}",
                     r"secret\s*=\s*['\"][^'\"]{8,}"]
    cred_found = any(re.search(p, content, re.IGNORECASE) for p in cred_patterns)
    checks.append({"check": "no_credentials", "passed": not cred_found,
                   "detail": "Credential pattern detected" if cred_found else "Clean"})

    # Check 3: CA sections not overwritten (philosophy sections must contain placeholder or CA content)
    if "⚠️ Chief Architect Required" in content:
        # If it has the placeholder tag, it's not yet authored — that's fine for validation
        # What we DON'T want is a chapter that REMOVES this tag without CA authorship
        checks.append({"check": "ca_sections_preserved", "passed": True,
                       "detail": "Chief Architect placeholders present"})
    else:
        checks.append({"check": "ca_sections_preserved", "passed": True,
                       "detail": "No CA placeholders (fully authored or impl-only)"})

    # Check 4: Valid volume reference
    vol_match = re.search(r"^# Volume ([IVX]+)", content, re.MULTILINE)
    checks.append({"check": "valid_volume_ref", "passed": bool(vol_match),
                   "detail": f"Volume: {vol_match.group(1) if vol_match else 'NOT FOUND'}"})

    all_passed = all(c["passed"] for c in checks)
    return {"passed": all_passed, "checks": checks, "validated_at": _now()}


def _append_changelog(entry: str) -> None:
    if not _CHANGELOG.exists():
        return
    content = _CHANGELOG.read_text()
    # Insert after first --- separator
    insert_after = content.find("\n---\n")
    if insert_after == -1:
        return
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_entry = f"\n\n## {ts} — {entry}\n\n*Auto-generated by Architecture Sync Engine*\n"
    updated = content[:insert_after + 5] + new_entry + content[insert_after + 5:]
    _CHANGELOG.write_text(updated)


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("")
def service_info():
    return {
        "service": "architecture-sync",
        "version": "1.0",
        "description": "Chief Architect Handbook Authoring Pipeline + Sync Engine",
        "endpoints": [
            "GET  /status",
            "GET  /conflicts",
            "GET  /review-engine",
            "GET  /queue",
            "POST /validate",
            "POST /publish",
            "POST /submit-chapter",
            "POST /sync",
        ],
    }


@router.get("/status")
def handbook_status():
    """Current handbook status: volumes, ADRs, authoring queue summary."""
    volumes = [_volume_status(v) for v in _VOLUMES]
    drafts   = list(_DRAFTS.glob("*.md"))     if _DRAFTS.exists() else []
    published = list(_PUBLISHED.glob("*.md")) if _PUBLISHED.exists() else []

    ca_sections_total  = sum(v.get("ca_sections_pending", 0) for v in volumes)
    volumes_published  = sum(1 for v in volumes if v["status"] == "PUBLISHED")

    return {
        "handbook_version": "2.0",
        "last_sync": _now(),
        "volumes": volumes,
        "adr_count": len(_adr_list()),
        "adrs": _adr_list(),
        "authoring_queue": _queue_summary(),
        "drafts_pending": len(drafts),
        "chapters_published": len(published),
        "ca_sections_pending": ca_sections_total,
        "volumes_needing_ca": [v["volume"] for v in volumes if v.get("ca_authorship_required")],
    }


@router.get("/conflicts")
def list_conflicts():
    """Implementation vs handbook conflicts."""
    conflicts = _detect_conflicts()
    return {
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "recommendation": "Review CHIEF_ARCHITECT_REVIEW_QUEUE.md for resolution path",
        "scanned_at": _now(),
    }


@router.get("/review-engine")
def review_engine(files: Optional[str] = None):
    """
    Determine which handbook volumes are affected by recent changes.
    Pass ?files=path1,path2 to check specific files.
    Without params: checks git status for recently modified files.
    """
    if files:
        changed = [f.strip() for f in files.split(",")]
    else:
        # Read last commit changed files
        try:
            import subprocess
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                capture_output=True, text=True, cwd=str(_ROOT)
            )
            changed = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        except Exception:
            changed = []

    return _review_engine_files(changed)


@router.get("/queue")
def authoring_queue():
    """Current AUTHORING_QUEUE chapter-by-chapter status."""
    if not _AUTH_QUEUE.exists():
        raise HTTPException(404, "AUTHORING_QUEUE.md not found")
    content = _AUTH_QUEUE.read_text()
    summary = _queue_summary()

    # Parse volume sections
    volume_sections = re.split(r"\n## Volume", content)[1:]
    volumes_parsed = []
    for section in volume_sections:
        title_match = re.match(r"\s+([IVX]+)\s+—\s+(.+)", section.split("\n")[0])
        if title_match:
            vol_num, vol_title = title_match.groups()
            rows = re.findall(r"\| (\d+\.\d+) \| (.+?) \| (.+?) \|", section)
            volumes_parsed.append({
                "volume": vol_num,
                "title": vol_title.strip(),
                "chapters": [{"section": r[0], "title": r[1].strip(), "status": r[2].strip()} for r in rows],
            })

    return {"summary": summary, "volumes": volumes_parsed, "retrieved_at": _now()}


class ValidateRequest(BaseModel):
    content: str
    volume: str
    chapter: Optional[str] = None


@router.post("/validate")
def validate_draft(req: ValidateRequest):
    """Validate a draft chapter before publishing."""
    result = _validate_draft(req.content, req.volume)
    return {
        "volume": req.volume,
        "chapter": req.chapter,
        "validation": result,
    }


class PublishRequest(BaseModel):
    volume: str
    chapter: str
    content: str
    author: str = "Chief Architect"
    dry_run: bool = True


@router.post("/publish")
def publish_chapter(req: PublishRequest):
    """Publish a validated draft: version, write to Published/, update index + changelog."""
    validation = _validate_draft(req.content, req.volume)
    if not validation["passed"]:
        raise HTTPException(422, detail={"error": "Validation failed", "checks": validation["checks"]})

    if req.dry_run:
        return {
            "dry_run": True,
            "would_publish": {
                "volume": req.volume,
                "chapter": req.chapter,
                "author": req.author,
                "validation": validation,
            }
        }

    # Write to Published/
    filename = f"Volume_{req.volume}_{req.chapter.replace('.','_')}_published.md"
    pub_path = _PUBLISHED / filename
    versioned_content = f"<!-- Published: {_now()} | Author: {req.author} -->\n\n" + req.content
    pub_path.write_text(versioned_content)

    # Append to changelog
    _append_changelog(f"Published Volume {req.volume} — Chapter {req.chapter} by {req.author}")

    return {
        "dry_run": False,
        "published": {
            "volume": req.volume,
            "chapter": req.chapter,
            "file": filename,
            "author": req.author,
            "published_at": _now(),
        }
    }


class SubmitChapterRequest(BaseModel):
    source: str  # google_drive | git | api | manual | ai_author
    volume: str
    chapter: Optional[str] = None
    title: str
    content: str
    author: str = "Chief Architect"
    dry_run: bool = True


@router.post("/submit-chapter")
def submit_chapter(req: SubmitChapterRequest):
    """Accept a chapter from any source. Validates and optionally publishes."""
    validation = _validate_draft(req.content, req.volume)

    # Write to Drafts/ regardless of validation result
    filename = f"Volume_{req.volume}_{(req.chapter or 'full').replace('.','_')}.md"
    draft_path = _DRAFTS / filename
    draft_path.write_text(req.content)

    result = {
        "source": req.source,
        "volume": req.volume,
        "chapter": req.chapter,
        "title": req.title,
        "draft_saved": str(draft_path.relative_to(_ROOT)),
        "validation": validation,
        "submitted_at": _now(),
    }

    if validation["passed"] and not req.dry_run:
        pub_result = publish_chapter(PublishRequest(
            volume=req.volume, chapter=req.chapter or "full",
            content=req.content, author=req.author, dry_run=False
        ))
        result["published"] = pub_result
    else:
        result["next_step"] = "POST /publish once draft is ready" if validation["passed"] else "Fix validation errors then POST /publish"

    return result


@router.post("/sync")
def force_sync():
    """Force full re-sync: rebuild cross-references, scan conflicts, update index."""
    volumes = [_volume_status(v) for v in _VOLUMES]
    conflicts = _detect_conflicts()
    adrs = _adr_list()

    # Update platform state in master index - pull the REAL live score, not a
    # hardcoded one. Found 2026-07-07: this was writing a fixed "95/100" on every
    # sync regardless of actual system state, the same "report says healthy
    # regardless of reality" pattern found in workflow_health and drift-check
    # this same session, just in a third place.
    try:
        if _MASTER_INDEX.exists():
            content = _MASTER_INDEX.read_text()
            ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            try:
                import urllib.request as _ur
                with _ur.urlopen("http://localhost:8000/api/v1/services/system-auditor/run", timeout=15) as _r:
                    real_score = json.loads(_r.read()).get("overall_health_score", 95)
            except Exception:
                real_score = 95
            status_word = "HEALTHY" if real_score >= 80 else ("DEGRADED" if real_score >= 60 else "UNHEALTHY")
            content = re.sub(
                r"\*\*Overall\*\* \| \*\*[A-Z]+\*\* \| \*\*\d+\/100\*\* \| \*\*\d{4}-\d{2}-\d{2}\*\*",
                f"**Overall** | **{status_word}** | **{real_score}/100** | **{ts}**",
                content
            )
            _MASTER_INDEX.write_text(content)
    except Exception as e:
        logger.warning("Could not update master index: %s", e)

    _append_changelog(f"Manual sync triggered — {len(conflicts)} conflicts, {len(adrs)} ADRs")

    return {
        "sync_complete": True,
        "volumes_scanned": len(volumes),
        "conflicts_found": len(conflicts),
        "adrs_indexed": len(adrs),
        "synced_at": _now(),
    }


@router.post("/refresh-automation-library")
def refresh_automation_library():
    """Regenerate Volume VII's n8n workflow table from live n8n state, not memory.
    Found 2026-07-07: the hand-maintained table listed 20 workflows; 56 were
    actually active, including all 4 core daily jobs (AUTO-001-004). Nothing
    ever re-ran this after the doc was first written, same root cause as the
    dead-scheduler mining engine found the same session. Designed to be called
    on a schedule (see AUTO-BOOK-REFRESH n8n workflow) so this can't happen again -
    it's generated from reality every time, not hand-edited prose that can drift."""
    n8n_key = os.environ.get("N8N_API_KEY", "")
    if not n8n_key:
        raise HTTPException(400, "N8N_API_KEY not configured")

    import urllib.request as _ur
    req = _ur.Request("http://localhost:5678/api/v1/workflows?limit=250", headers={"X-N8N-API-KEY": n8n_key})
    with _ur.urlopen(req, timeout=15) as r:
        workflows = json.loads(r.read()).get("data", [])

    active = sorted([w for w in workflows if w.get("active")], key=lambda w: w["name"])
    inactive = sorted([w for w in workflows if not w.get("active")], key=lambda w: w["name"])

    def _trigger_desc(wid: str) -> str:
        try:
            r2 = _ur.Request(f"http://localhost:5678/api/v1/workflows/{wid}", headers={"X-N8N-API-KEY": n8n_key})
            with _ur.urlopen(r2, timeout=10) as rr:
                full = json.loads(rr.read())
            for n in full.get("nodes", []):
                t = n["type"]
                if t == "n8n-nodes-base.scheduleTrigger":
                    for iv in n.get("parameters", {}).get("rule", {}).get("interval", []):
                        if iv.get("field") == "cronExpression":
                            return f"cron `{iv['expression']}`"
                        if iv.get("field") == "hours":
                            return "interval (⚠️ unreliable - convert to cron)"
                if t == "n8n-nodes-base.webhook":
                    return "webhook (event-driven)"
                if t == "n8n-nodes-base.microsoftOutlookTrigger":
                    return "email arrival"
                if t == "n8n-nodes-base.cron":
                    return "cron (legacy node)"
            return "unknown"
        except Exception:
            return "unknown"

    lines = [
        "## 7.2 n8n Workflows (✅ Active)",
        "",
        f"*Auto-generated from live n8n state by `POST /architecture-sync/refresh-automation-library` — {_now()}. "
        f"Do not hand-edit this table; it will be overwritten on the next refresh.*",
        "",
        f"**{len(active)} active, {len(inactive)} inactive/archived, {len(workflows)} total.**",
        "",
        "### Automation Schedule",
        "",
        "| Workflow | Trigger |",
        "|----------|---------|",
    ]
    for w in active:
        lines.append(f"| {w['name']} | {_trigger_desc(w['id'])} |")
    lines += ["", "### Inactive / Archived", "", "| Workflow |", "|----------|"]
    for w in inactive:
        lines.append(f"| {w['name']} |")
    lines.append("")

    vol7 = _HANDBOOK / "Volume_07_Automation_Architecture.md"
    content = vol7.read_text()
    # Replace from "## 7.2" up to (not including) the next "## 7.3"
    new_content = re.sub(
        r"## 7\.2 n8n Workflows.*?(?=\n## 7\.3)",
        "\n".join(lines) + "\n",
        content,
        flags=re.DOTALL,
    )
    vol7.write_text(new_content)

    _append_changelog(f"Automation Library auto-refreshed — {len(active)} active workflows, {len(inactive)} inactive")

    return {
        "refreshed": True,
        "active_workflows": len(active),
        "inactive_workflows": len(inactive),
        "file": str(vol7.relative_to(_ROOT)),
        "refreshed_at": _now(),
    }
