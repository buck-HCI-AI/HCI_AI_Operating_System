#!/usr/bin/env python3
"""
HCI Agent Handoff Bus Processor
Scans Inbox/, validates, routes, and archives agent handoff files.
Usage: python3 handoff_processor.py [--dry-run] [--file path/to/file.md]
"""
import os, sys, json, shutil, argparse, requests
from datetime import datetime, timezone
from pathlib import Path

BASE        = Path(__file__).parent
REPO_ROOT   = BASE.parent.parent   # HCI_AI_Operating_System/
INBOX       = BASE / "Inbox"
PROCESSING  = BASE / "Processing"
PROCESSED   = BASE / "Processed"
FAILED      = BASE / "Failed"
ARCHIVE     = BASE / "Archive"
INDEX       = BASE / "HANDOFF_INDEX.md"

API_BASE    = "http://localhost:8000/api/v1"
API_KEY     = "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"
NTFY_TOPIC  = "https://ntfy.sh/hci-executive"

# Fields that must exist; created_at and summary are auto-injected if absent
REQUIRED_FIELDS = [
    "source_agent", "destination_agent", "document_type", "priority", "status",
]

# System-specific routing for browser_discovery documents
SYSTEM_CURRENT_DIRS = {
    "houzz":           REPO_ROOT / "Architecture/Platform_Intelligence/Houzz/Current",
    "houzz pro":       REPO_ROOT / "Architecture/Platform_Intelligence/Houzz/Current",
    "hubspot":         REPO_ROOT / "Architecture/Platform_Intelligence/HubSpot/Current",
    "quickbooks":      REPO_ROOT / "Architecture/Platform_Intelligence/QuickBooks/Current",
    "google drive":    REPO_ROOT / "Architecture/Platform_Intelligence/GoogleDrive/Current",
    "microsoft365":    REPO_ROOT / "Architecture/Platform_Intelligence/Microsoft365/Current",
    "outlook":         REPO_ROOT / "Architecture/Platform_Intelligence/Microsoft365/Current",
    "n8n":             REPO_ROOT / "Architecture/Platform_Intelligence/n8n/Current",
    "postgresql":      REPO_ROOT / "Architecture/Platform_Intelligence/PostgreSQL/Current",
    "buildingconnected": REPO_ROOT / "Architecture/Platform_Intelligence/BuildingConnected/Current",
    "procore":         REPO_ROOT / "Architecture/Platform_Intelligence/Procore/Current",
}

ROUTING = {
    "browser_discovery":            None,   # resolved dynamically by related_system
    "platform_watch":               REPO_ROOT / "Architecture/Platform_Intelligence",
    "houzz_export":                 REPO_ROOT / "Architecture/Platform_Intelligence/Houzz/Current",
    "hubspot_export":               REPO_ROOT / "Architecture/Platform_Intelligence/HubSpot/Current",
    "platform_opportunity_report":  REPO_ROOT / "Architecture/Platform_Intelligence",
    "business_process_architecture": REPO_ROOT / "Architecture/Platform_Intelligence",
    "chief_architect_directive":    REPO_ROOT / "Architecture/Handbook/Drafts",
    "architecture_chapter":         REPO_ROOT / "Architecture/Handbook/Drafts",
    "implementation_request":       None,   # append to STRATEGIC_BACKLOG
    "approval_request":             None,   # POST to executive inbox API
    "executive_brief":              REPO_ROOT / "Architecture/Handbook/Published",
}

VALID_TYPES = list(ROUTING.keys())


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.strip().startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    import re
    header = {}
    for line in parts[1].strip().splitlines():
        m = re.match(r'^(\w[\w_]*)\s*:\s*(.+)$', line.strip())
        if m:
            k, v = m.group(1).strip(), m.group(2).strip()
            if v.lower() in ("true", "false"):
                v = v.lower() == "true"
            header[k] = v
    return header, parts[2].strip()


def parse_handoff(file_path: Path) -> tuple[dict, str]:
    content = file_path.read_text(encoding="utf-8")
    if content.strip().startswith("{"):
        try:
            data = json.loads(content)
            return data, data.get("payload", "")
        except json.JSONDecodeError:
            pass
    return _parse_frontmatter(content)


def _auto_inject(header: dict, file_path: Path) -> dict:
    """Inject created_at and summary if absent — Browser Claude files often omit these."""
    if "created_at" not in header:
        header["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if "summary" not in header:
        system = header.get("related_system", header.get("document_type", "unknown"))
        header["summary"] = f"Browser discovery — {system} — auto-ingested {header['created_at']}"
    return header


def _system_dest(header: dict) -> Path:
    """Resolve destination directory for browser_discovery by related_system."""
    system = header.get("related_system", "").lower().strip()
    for key, path in SYSTEM_CURRENT_DIRS.items():
        if key in system:
            return path
    # Fallback: parse from filename BROWSER_HANDOFF_{SYSTEM}_*
    return REPO_ROOT / "Architecture/Platform_Intelligence"


def validate_handoff(header: dict) -> tuple[bool, str]:
    if not header:
        return False, "Empty header — cannot parse handoff"
    missing = [f for f in REQUIRED_FIELDS if f not in header]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    doc_type = header.get("document_type", "")
    if doc_type not in VALID_TYPES:
        return False, f"Unknown document_type '{doc_type}'. Valid: {', '.join(VALID_TYPES)}"
    return True, "valid"


def route_handoff(file_path: Path, header: dict, payload: str, dry_run: bool) -> str:
    doc_type = header["document_type"]
    source   = header.get("source_agent", "unknown")
    summary  = header.get("summary", "")

    # Dynamic routing for browser_discovery
    if doc_type == "browser_discovery":
        dest_dir = _system_dest(header)
        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / file_path.name
            # Archive any existing file with same name before overwriting
            if dest_file.exists():
                system_key = header.get("related_system", "unknown").replace(" ", "")
                archive_dir = dest_dir.parent / "Archive"
                archive_dir.mkdir(exist_ok=True)
                ts_tag = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
                shutil.copy2(dest_file, archive_dir / f"{dest_file.stem}_{ts_tag}{dest_file.suffix}")
            shutil.copy2(file_path, dest_file)
        rel = dest_dir.relative_to(REPO_ROOT)
        return f"→ {rel}/{file_path.name}"

    dest_dir = ROUTING.get(doc_type)

    if dest_dir:
        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_dir / file_path.name)
        return f"→ {dest_dir.relative_to(REPO_ROOT)}/{file_path.name}"

    if doc_type == "implementation_request":
        backlog = REPO_ROOT / "Architecture/STRATEGIC_BACKLOG.md"
        title   = header.get("title", "Untitled")
        entry   = (f"\n\n### {title}\n"
                   f"*Source: {source} | {header.get('created_at', '')}*\n\n"
                   f"{payload[:1000]}\n")
        if not dry_run:
            with open(backlog, "a", encoding="utf-8") as f:
                f.write(entry)
        return "→ Appended to STRATEGIC_BACKLOG.md"

    if doc_type == "approval_request":
        if not dry_run:
            try:
                r = requests.post(
                    f"{API_BASE}/executive-inbox",
                    headers={"X-API-Key": API_KEY},
                    json={"title": header.get("title", summary), "summary": summary, "source": source},
                    timeout=5,
                )
                if r.status_code not in (200, 201):
                    return f"→ API failed ({r.status_code}) — flagged for manual review"
            except Exception as e:
                return f"→ API unreachable ({e}) — flagged for manual review"
        return "→ Posted to Executive Inbox"

    return f"→ No routing configured for {doc_type}"


def update_index(entry: dict, dry_run: bool):
    ts    = entry["timestamp"]
    name  = entry["filename"]
    dtype = entry["document_type"]
    src   = entry["source_agent"]
    st    = entry["status"]
    dest  = entry.get("destination", "")
    line  = f"| {ts} | {name} | {dtype} | {src} | {st} | {dest} |\n"
    if not dry_run:
        if not INDEX.exists():
            INDEX.write_text(
                "# Agent Handoff Bus Index\n*Updated automatically by handoff_processor.py*\n\n"
                "| Timestamp | File | Type | Source Agent | Status | Destination |\n"
                "|-----------|------|------|-------------|--------|-------------|\n"
            )
        with open(INDEX, "a") as f:
            f.write(line)


def _notify(message: str, title: str = "Agent Handoff Bus"):
    try:
        requests.post(NTFY_TOPIC, data=message.encode(),
                      headers={"Title": title, "Content-Type": "text/plain"}, timeout=5)
    except Exception:
        pass


def process_file(file_path: Path, dry_run: bool) -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    print(f"\nProcessing: {file_path.name}")

    if not dry_run:
        shutil.move(str(file_path), PROCESSING / file_path.name)
        file_path = PROCESSING / file_path.name

    header, payload = parse_handoff(file_path)

    # Auto-inject optional fields before validation
    if header:
        header = _auto_inject(header, file_path)

    valid, reason = validate_handoff(header)

    if not valid:
        print(f"  ❌ INVALID: {reason}")
        if not dry_run:
            shutil.move(str(file_path), FAILED / file_path.name)
        result = {"filename": file_path.name, "timestamp": ts,
                  "document_type": header.get("document_type", "unknown"),
                  "source_agent": header.get("source_agent", "unknown"),
                  "status": "FAILED", "destination": reason}
        update_index(result, dry_run)
        return result

    destination = route_handoff(file_path, header, payload, dry_run)
    print(f"  ✅ Routed {destination}")

    if not dry_run:
        shutil.move(str(file_path), PROCESSED / file_path.name)

    result = {"filename": file_path.name, "timestamp": ts,
              "document_type": header["document_type"],
              "source_agent": header.get("source_agent", "unknown"),
              "status": "PROCESSED", "destination": destination}
    update_index(result, dry_run)
    return result


def main():
    parser = argparse.ArgumentParser(description="HCI Agent Handoff Bus Processor")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--file", help="Process a specific file instead of scanning Inbox/")
    args = parser.parse_args()

    for d in [INBOX, PROCESSING, PROCESSED, FAILED, ARCHIVE]:
        d.mkdir(parents=True, exist_ok=True)

    if args.file:
        files = [Path(args.file)]
    else:
        files = list(INBOX.glob("*.md")) + list(INBOX.glob("*.json"))

    if not files:
        print("Inbox is empty — nothing to process.")
        return

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Processing {len(files)} file(s)...")
    results = [process_file(f, args.dry_run) for f in files]

    processed = [r for r in results if r["status"] == "PROCESSED"]
    failed    = [r for r in results if r["status"] == "FAILED"]

    types = ", ".join(sorted(set(r["document_type"] for r in processed))) or "—"
    summary = f"Handoff Bus: {len(processed)}/{len(results)} processed. Types: {types}."
    if failed:
        summary += f" Failed: {len(failed)} (see Failed/)."

    print(f"\n{summary}")
    if not args.dry_run and results:
        _notify(summary)


if __name__ == "__main__":
    main()
