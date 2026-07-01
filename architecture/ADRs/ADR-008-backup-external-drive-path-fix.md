---
id: ADR-008
title: Backup System — External Drive Detection Fix + Repo Rsync
status: accepted
date: 2026-06-30
author: Claude Code (session 2026-06-30)
tags: [backup, disaster-recovery, ops]
---

## Context

Buck asked to confirm continuous external-drive backups and an easy recovery path
for system failure or machine replacement. Auditing `03_Source_Code/scripts/backup.sh`
(the only backup mechanism actually installed as a launchd job — `com.hci.backup`,
daily 02:00) found:

1. **The external drive check never passed.** The drive mounts as `/Volumes/HCI_AI_DEV `
   with a trailing space (confirmed via raw byte inspection of `ls -la /Volumes/`),
   but the script hardcoded `/Volumes/HCI_AI_DEV/backups` (no trailing space). The
   `-d`/`-w` check on that exact path always failed, so every run silently fell back
   to `~/HCI_Backups` on the internal disk — an off-machine backup never actually
   existed, despite the drive being plugged in on many nights.
2. **`Operations_Manual/Chapter_23_Backup_Recovery.md` (v1.0) documented a different,
   never-built mechanism** (`hci_daily_backup.sh` + `SETUP_DAILY_BACKUP.command` +
   a second launchd job `com.hci.daily.backup`) that does not exist on disk and was
   never loaded. The chapter described aspirational infrastructure as if it were live.
3. **Pruning silently failed.** `head -n -7` is a GNU coreutils extension; macOS's
   BSD `head` errors on negative counts. Under `set -e` this should have crashed the
   script, but the failure was inside a pipeline so `set -e` didn't propagate it —
   backups simply never got pruned (a disk-space risk, not a data-loss risk).
4. **Source code/docs were never backed up at all** — the script only covered
   Postgres, Qdrant, and a MinIO manifest, not the repo itself.

## Decision

1. Replace the exact-path check with a glob match (`/Volumes/HCI_AI_DEV*`) so the
   script tolerates the trailing space, or macOS appending `1`/`2` on a name
   collision, without needing to know the exact mounted name in advance.
2. Add a repo rsync step (excludes `.git`, `node_modules`, `__pycache__`) so
   uncommitted/untracked work is captured, not just what's been committed.
3. Fix the pruning loop with a portable bash array approach (no GNU-only flags).
4. Rewrite Chapter 23 to describe only the system that actually exists, and add a
   concrete "new machine / system failure" recovery walkthrough (restore Postgres
   dump, restore Qdrant snapshots, re-register the Telegram webhook via
   `POST /gateway/telegram/register-webhook`, verify via `GET /gateway/ai/warm-start`).
5. Add `~/Desktop/RUN_BACKUP_NOW.command` — a double-click manual trigger, per the
   project's standing rule that Buck gets runnable files, not copy/paste instructions.

## Constraints / Known Remaining Gaps

- The fix only helps when the drive is physically connected — confirmed
  intermittent during this session (mounted, then unmounted, within the same
  hour). No code fix can address a drive that isn't plugged in; flagged to Buck.
- MinIO backs up a manifest (listing) only, not object contents — restoring actual
  MinIO objects from backup is not currently possible. Documented as an open gap,
  not fixed here (out of scope for a P0-adjacent request; flagged for a future pass).
- GitHub (`origin`) is a second, genuinely off-machine backup layer for code, but
  only for what's been pushed — local `main` was several commits ahead of
  `origin/main` at audit time. Pushing is gated per CLAUDE.md; raised to Buck
  separately rather than pushed unilaterally.
