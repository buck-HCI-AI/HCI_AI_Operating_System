#!/usr/bin/env python3
"""
HCI Agent Handoff Intake Watcher
Watches ~/Downloads for BROWSER_HANDOFF_*.md files and auto-routes them
into the Agent Handoff Bus without Buck involvement.

Triggered by launchd WatchPaths on ~/Downloads.
"""
import os, sys, shutil, subprocess, time
from pathlib import Path
from datetime import datetime

DOWNLOADS   = Path.home() / "Downloads"
INBOX       = Path("/Users/buckadams/HCI_AI_Operating_System/Architecture/Agent_Handoff/Inbox")
PROCESSOR   = Path("/Users/buckadams/HCI_AI_Operating_System/Architecture/Agent_Handoff/handoff_processor.py")
LOG_FILE    = Path("/Users/buckadams/HCI_AI_Operating_System/infrastructure/logs/handoff_intake.log")

PATTERN_PREFIXES = ["BROWSER_HANDOFF_", "HCI_HANDOFF_", "AGENT_HANDOFF_"]


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def is_handoff_file(path: Path) -> bool:
    if path.suffix.lower() not in (".md", ".json"):
        return False
    return any(path.name.startswith(pfx) for pfx in PATTERN_PREFIXES)


def intake_file(src: Path):
    dest = INBOX / src.name
    INBOX.mkdir(parents=True, exist_ok=True)

    # If a file with same name already in inbox, add timestamp suffix
    if dest.exists():
        ts = datetime.now().strftime("%H%M%S")
        dest = INBOX / f"{src.stem}_{ts}{src.suffix}"

    shutil.move(str(src), dest)
    log(f"Moved {src.name} → Inbox/{dest.name}")

    # Run the processor
    result = subprocess.run(
        [sys.executable, str(PROCESSOR)],
        capture_output=True, text=True
    )
    log(f"Processor: {result.stdout.strip()}")
    if result.returncode != 0:
        log(f"Processor stderr: {result.stderr.strip()}")


def scan_downloads():
    """One-shot scan — called by launchd on WatchPaths trigger."""
    found = [p for p in DOWNLOADS.glob("*") if p.is_file() and is_handoff_file(p)]
    if not found:
        log("Downloads scan: no handoff files found")
        return
    for p in found:
        try:
            intake_file(p)
        except Exception as e:
            log(f"ERROR processing {p.name}: {e}")


if __name__ == "__main__":
    log("Handoff intake watcher triggered")
    scan_downloads()
