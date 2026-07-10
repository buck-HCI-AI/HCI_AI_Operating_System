# ADR-018 — Unattended Restart/Recovery: Monitor Coverage Gaps Closed

**Date:** 2026-07-10
**Status:** Accepted, live
**Driver:** Buck stepping away from the Mac Air; explicitly asked to prep the system
so it self-recovers from crashes/reboots without him having to intervene. Selected
"Restart/recovery system" as priority via AskUserQuestion over finishing Role
Onboarding or the remaining drift-check findings.

## Context

Audited every launchd job (`api-server`, `mcp-server`, `ngrok`, `monitor`,
`drive-watcher`, `handoff-intake`, `morning-brief`, `backup`) plus Docker container
restart policies and `scripts/monitor.sh` (the existing 5-minute health-check loop)
to answer: does this system come back on its own after a crash or full reboot?

**What was already solid, no changes needed:**
- `api-server`, `mcp-server`: launchd `RunAtLoad: true` + `KeepAlive: true` — process
  crash auto-restarts immediately, survives reboot.
- `hci_postgres`, `hci_redis`, `hci_minio`, `hci_qdrant`, `n8n` containers: all
  `restart: unless-stopped` at the Docker level. Docker Desktop is a macOS login item,
  so containers come back automatically after a full machine reboot.
- `monitor.sh` (every 5 min, `RunAtLoad: true`): already checked API health with
  auto-restart (3 attempts, then email alert) and disk usage.

**Real gaps found, not previously covered by anything:**
1. **ngrok was never monitored.** GBT's entire connection to the system is through
   the ngrok tunnel — this session already had one real GBT outage
   (schema-version-lock, unrelated cause) and separately the drift-check history
   flags 3-7s gateway latency as a past root cause of a GBT failure. If the ngrok
   process died, nothing would restart it or tell Buck — GBT would just silently go
   dark with no alert distinguishing "ngrok down" from "GBT itself confused."
2. **mcp-server was never monitored.** Same blind spot — process could die and
   nothing would notice or restart it.
3. **Docker container down was detected but never self-healed** — `monitor.sh` would
   email Buck "containers down, run `docker compose up -d` yourself" instead of just
   running it.
4. **`com.hci.drive-watcher`'s `WatchPaths` never matched the real mount point.**
   Confirmed via `python3 -c "import os; print(os.listdir('/Volumes'))"` that the
   actual mount name is `HCI_AI_DEV ` (trailing space); the plist watched
   `HCI_AI_DEV` (no space). The watcher had never fired even once, including earlier
   in this same session when the drive was mounted and connected.

## Decision

Extended `scripts/monitor.sh` (still on the same 5-min `StartInterval` +
`RunAtLoad`) with three new checks, each following the existing pattern
(detect → attempt automatic fix → re-check → alert only if the fix didn't work):

- **ngrok**: `curl http://localhost:4040/api/tunnels` (ngrok's own local API) — if
  not HTTP 200, `launchctl kickstart -k gui/$(id -u)/com.ngrok.hci`, re-check,
  alert only on failure. Alert text explicitly says "GBT/Chief Architect's only path
  into the system" so Buck knows the blast radius without guessing.
- **mcp-server**: `curl http://localhost:8080/` (any HTTP response counts as "up" —
  it 404s on `/` normally, that's fine; `000`/connection-refused means the process is
  actually gone) — same kickstart-and-recheck pattern.
- **Docker containers**: now runs `docker compose up -d` immediately on detecting any
  container down, waits 10s, re-checks, and only alerts if containers are *still*
  down after the self-heal attempt (previously alerted immediately with no attempt
  to fix it).

Fixed `com.hci.drive-watcher`'s `WatchPaths` to include both the space and no-space
variants of the mount path, then reloaded the launchd job
(`launchctl unload` + `launchctl load`). This was a pure detection fix — did **not**
touch `start_with_drive.sh`'s existing safety guard, which still aborts if the 4
required folders (`03_MinIO_Data`, `05_Docker_Volumes/{postgres,redis,qdrant}`)
aren't present on the drive. Confirmed those folders do not yet exist (drive is
~999KB, essentially empty, `setup_storage_drive.sh` has never been run) — so even
now that the watcher can fire correctly, it will safely no-op with a clear error log
rather than attempt a migration against missing folders.

## Explicitly deferred, not part of this fix

The external-drive full storage migration (`setup_storage_drive.sh` →
`migrate_volumes.sh` → `docker-compose.storage.yml`) is a real, well-designed,
already-built mechanism for relocating Postgres/Redis/Qdrant/MinIO's actual data to
`/Volumes/HCI_AI_DEV`. It is **not** wired to auto-fire as part of this ADR, and
should not be, for three concrete reasons:

1. Full Disk Access has not been granted to Terminal yet (Buck's action, System
   Settings > Privacy & Security), so the drive still isn't reliably usable by shell
   tools.
2. The drive has no folder structure yet (`setup_storage_drive.sh` never run) and no
   copied data (`migrate_volumes.sh` never run).
3. `migrate_volumes.sh` runs `docker compose down` — it stops every live service
   as its first step. That's a deliberate, one-time cutover Buck should be present
   for, not something that should ever fire unattended off a drive-mount event while
   he's away. This is a genuine production migration, not a backup copy.

If/when Buck wants to do this migration, the sequence is: grant Full Disk Access →
`bash infrastructure/setup_storage_drive.sh` → `bash infrastructure/migrate_volumes.sh`
→ verify data → switch over to `docker-compose.storage.yml`. Recommend treating this
as its own scheduled, attended session, not part of "recovery while I'm away."

## Verification

Ran `scripts/monitor.sh` live end-to-end after the edit — all 6 checks (API, 4
containers, ngrok, mcp-server, disk) passed cleanly with no alert fired, confirming
the new checks don't false-positive against the actual healthy system state.
`bash -n` syntax-checked before the live run.
