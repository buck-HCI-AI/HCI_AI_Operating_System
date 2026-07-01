# Chapter 23 — Backup & Recovery
*HCI AI Operations Manual — Part II: AI System Operations*
**Author:** Claude Code | **Version:** 2.0 | **Date:** 2026-06-30

---

## 23.1 What Actually Runs (corrects v1.0, which described a system that was never built)

One script, one launchd job. That is the entire backup system:

- **Script:** `03_Source_Code/scripts/backup.sh`
- **Scheduler:** launchd job `com.hci.backup` (`~/Library/LaunchAgents/com.hci.backup.plist`), daily at 02:00
- **Manual trigger:** double-click `RUN_BACKUP_NOW.command` on the Desktop, any time

(v1.0 of this chapter described a second mechanism — `hci_daily_backup.sh` + `SETUP_DAILY_BACKUP.command` + a `com.hci.daily.backup` launchd job — that was documented but never actually created. There is no dual system. Ignore any prior reference to it.)

## 23.2 What Gets Backed Up

Every night at 2:00 AM, `backup.sh` runs four steps:

1. **Repo rsync** — full source tree (code, docs, Operations Manual, Architecture) minus `.git`/`node_modules`/`__pycache__`. Includes uncommitted/untracked files, so work-in-progress isn't lost even before it's committed.
2. **Postgres dump** — full `hci_os` database via `pg_dump -Fc` (compressed custom format).
3. **Qdrant snapshots** — all 13 vector collections (vendor_memory, project_memory, drive_memory, etc.).
4. **MinIO manifest** — object listing (not object contents — see 23.7).

Retention: 7 rolling days, oldest pruned automatically.

## 23.3 Destination — Read This Carefully

**Primary:** the external drive, auto-detected by glob match on `/Volumes/HCI_AI_DEV*`.

The drive's actual mount name is `HCI_AI_DEV ` **with a trailing space** — macOS assigns this, not us. The original script hardcoded the exact path without the trailing space, so the primary-destination check *always failed silently* and every backup since this was set up went to the fallback location instead. **Fixed 2026-06-30** (ADR-008) — the script now glob-matches any volume starting with `HCI_AI_DEV`, so it works regardless of trailing spaces or macOS renaming a duplicate to `HCI_AI_DEV 1`, etc.

**This only helps if the drive is actually plugged in.** As of this fix, the drive was mounted only intermittently during the session it was diagnosed in. If nightly backups matter, the drive needs to stay connected, or the fallback below needs to be treated as the real primary.

**Fallback (used whenever the drive isn't mounted):** `~/HCI_Backups/YYYY-MM-DD/` on the internal disk. This is NOT off-machine and does not protect against disk failure, theft, or loss of the machine — it only protects against accidental deletion/corruption of live data while the machine itself is fine.

## 23.4 Manual Backup (Any Time)

Double-click **`RUN_BACKUP_NOW.command`** on the Desktop. No Terminal, no copy-pasting commands.

Or from Claude Code / Terminal:
```bash
bash /Users/buckadams/HCI_AI_Operating_System/03_Source_Code/scripts/backup.sh
```

## 23.5 Verifying Backups

```bash
# Is the external drive currently the destination, or did it fall back?
ls /Volumes/ | grep -i HCI_AI_DEV || echo "Drive not mounted — backups are going to ~/HCI_Backups only"

# Today's backup present?
TODAY=$(date +%Y%m%d)
ls ~/HCI_Backups/$TODAY 2>/dev/null || ls /Volumes/HCI_AI_DEV*/backups/$TODAY 2>/dev/null || echo "NO BACKUP TODAY"
```

Or ask Claude Code: "check today's backup" — it will run the same check.

## 23.6 Recovery — New Machine / System Failure ("easy mini setup")

Everything needed to stand the system back up on a new machine (e.g. the planned Mac mini migration) lives in two places: **GitHub** (code, if pushed — see 23.8) and **the latest backup** (DB + vectors + anything not yet pushed).

1. Clone the repo: `git clone https://github.com/buck-HCI-AI/HCI_AI_Operating_System.git`
2. If the latest backup has newer/uncommitted work than GitHub, copy it in: `rsync -a <backup>/repo/ ~/HCI_AI_Operating_System/`
3. Install Docker, Python 3.13, ngrok.
4. Start Postgres/Qdrant/MinIO containers, then restore:
   ```bash
   docker exec -i hci_postgres pg_restore -U hci_admin -d hci_os < <backup>/postgres_TIMESTAMP.dump
   # Qdrant: POST each *.snapshot file to /collections/{name}/snapshots/upload
   ```
5. Copy `.env` from the backup's `repo/.env` (it's included in the rsync — keep the backup drive physically secure).
6. Start the API (`uvicorn api.main:app`), re-point ngrok, then `POST /gateway/telegram/register-webhook` to reconnect Telegram (this endpoint exists specifically so this step doesn't require manual Telegram API calls — see AI_TEAM/WARM_START.md).
7. Call `GET /gateway/ai/warm-start` to confirm the system sees current state — active projects, pending approvals, agent heartbeats.

This is the same recovery path regardless of *why* you're rebuilding — disk failure, migration to a new machine, or a fresh dev environment.

## 23.7 What Is NOT Backed Up

| Data | Where It Lives | Why Not Backed Up |
|------|---------------|-----------------|
| MinIO object contents | docker volume | Only a manifest (listing) is backed up, not the objects themselves — restoring MinIO content after a real loss is not currently possible from backup alone. Flagged as a gap. |
| Redis cache | docker volume | Ephemeral by design — auto-rebuilds |
| ChatGPT conversation history | ChatGPT cloud | Outside our control — key decisions should be filed as ADRs/handoffs, not left only in chat |
| Anything not yet committed AND not yet backed up | — | Repo rsync (23.2 step 1) covers the gap between "written" and "committed," but only from the last backup run — work done and lost within the same backup window (up to 24h) is still at risk |

## 23.8 Second Backup Layer: GitHub

The repo has a GitHub remote (`origin`). This is a genuinely separate, off-machine copy of code — but **only for what's actually been pushed.** As of 2026-06-30, local `main` was found to be several commits ahead of `origin/main`, meaning recent work (including this session's AI Operations Control Plane build) existed only on the local machine and the local/external-drive backup, not on GitHub. Pushing is gated per CLAUDE.md (requires explicit go-ahead) — see the session's final report for the specific ask.

## 23.9 Before Any Destructive Operation

```bash
BACKUP_DIR="$HOME/HCI_Backups/pre_op_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
docker exec hci_postgres pg_dump -U hci_admin hci_os > "$BACKUP_DIR/db_snapshot.sql"
echo "Backup at: $BACKUP_DIR"
```

Required before: any `DROP TABLE`, `DELETE FROM` without `WHERE`, `TRUNCATE`, or `UPDATE` affecting more than 100 rows. No destructive operations without backup + Buck's confirmation. No exceptions.

---

*Cross-reference: Chapter 22 (Database), Chapter 26 (Emergency), Chapter 31 (Change Management), AI_TEAM/WARM_START.md (restart recovery for the AI team specifically, not the underlying data)*
