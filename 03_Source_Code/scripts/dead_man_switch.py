#!/usr/bin/env python3
"""Dead-man switch — fires INDEPENDENT of any agent session.

Built 2026-07-21 after a read-gap silently swallowed 8+ P0s all afternoon (BC/GBT
wrote to agent_messages; CODE's cycle never read that table). A dead-man switch
that CODE runs itself can't catch CODE failing to read - so this runs from
monitor.sh (launchd, every 5 min), checks for P0s that have gone unacknowledged
past a deadline, and Telegrams Buck directly. Dedup + re-alert state in a temp
file so it alerts once per message, then again every RE_ALERT_HOURS if still open.

Sources checked:
  1. agent_messages: priority P0, to CODE/ALL, status='pending', older than DEADLINE_MIN.
  2. coordination_documents: critical/high, target_agent set, unacked by target past deadline.
"""
import json, os, subprocess, sys, urllib.request, ssl, datetime

DEADLINE_MIN = 60
RE_ALERT_HOURS = 2
STATE_FILE = "/tmp/hci_deadman_alerted.json"
API = "http://localhost:8000/gateway/telegram/send"
KEY = "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"


def _psql(sql):
    r = subprocess.run(["docker", "exec", "hci_postgres", "psql", "-U", "hci_admin",
                        "-d", "hci_os", "-tAF|", "-c", sql], capture_output=True, text=True)
    return [ln for ln in r.stdout.strip().splitlines() if ln]


def _telegram(text):
    if os.environ.get("DEADMAN_DRYRUN") == "1":
        print("[dead-man DRYRUN] would send:\n" + text)
        return True
    body = json.dumps({"text": text, "agent": "dead_man_switch"}).encode()
    req = urllib.request.Request(API, data=body,
                                 headers={"X-API-Key": KEY, "Content-Type": "application/json"},
                                 method="POST")
    try:
        urllib.request.urlopen(req, context=ssl.create_default_context(), timeout=15)
        return True
    except Exception:
        # gateway on localhost usually has no TLS; retry without verify context
        try:
            urllib.request.urlopen(req, timeout=15); return True
        except Exception:
            return False


def main():
    unacked = []
    # 1. agent_messages P0 to CODE/ALL, pending, older than DEADLINE_MIN
    for row in _psql(
        f"SELECT message_id, from_agent, subject, "
        f"EXTRACT(EPOCH FROM (NOW()-timestamp_mt))/60 FROM agent_messages "
        f"WHERE to_agent IN ('CODE','ALL') AND status='pending' AND priority IN ('P0','critical') "
        f"AND timestamp_mt < NOW() - INTERVAL '{DEADLINE_MIN} minutes'"):
        p = row.split("|")
        if len(p) >= 4:
            unacked.append({"id": p[0], "src": "agent_messages", "from": p[1],
                            "subj": p[2][:70], "age_min": int(float(p[3]))})
    # 2. coordination_documents INBOUND to CODE only (target_agent='CODE'), unacked.
    # NOT any target - a CODE_TO_CA/CODE_TO_BUCK doc that its recipient hasn't
    # acked is the recipient's problem, not a CODE read-failure, and flagging
    # CODE's own outbound was a false-positive (found + fixed 2026-07-21). Team
    # coordination-doc ack SLAs are already covered by /gateway/admin/drift-check.
    for row in _psql(
        "SELECT cd.file_id, cd.source, cd.filename, "
        "EXTRACT(EPOCH FROM (NOW()-cd.drive_created_at))/60 "
        "FROM coordination_documents cd "
        "LEFT JOIN coordination_document_acks a ON a.file_id=cd.file_id AND a.agent='claude_code' "
        f"WHERE cd.priority IN ('critical','high') AND cd.target_agent='CODE' "
        f"AND a.agent IS NULL AND cd.drive_created_at < NOW() - INTERVAL '{DEADLINE_MIN} minutes'"):
        p = row.split("|")
        if len(p) >= 4:
            unacked.append({"id": p[0], "src": "coordination_documents", "from": p[1],
                            "subj": p[2][:70], "age_min": int(float(p[3]))})

    # dedup / re-alert state
    try:
        state = json.load(open(STATE_FILE))
    except Exception:
        state = {}
    now = datetime.datetime.now().timestamp()
    to_alert = []
    for u in unacked:
        last = state.get(u["id"])
        if last is None or (now - last) > RE_ALERT_HOURS * 3600:
            to_alert.append(u)
            state[u["id"]] = now
    # prune state entries no longer unacked
    live_ids = {u["id"] for u in unacked}
    state = {k: v for k, v in state.items() if k in live_ids}
    json.dump(state, open(STATE_FILE, "w"))

    if not to_alert:
        print(f"[dead-man] {len(unacked)} unacked P0(s), none newly alert-due")
        return
    lines = [f"DEAD-MAN SWITCH: {len(to_alert)} P0(s) unacknowledged >{DEADLINE_MIN} min "
             f"— an agent may not be reading its channel.", ""]
    for u in to_alert:
        lines.append(f"• [{u['from']}->{u['src']}] {u['subj']} (unread {u['age_min']} min)")
    lines.append("")
    lines.append("If CODE is running it should have acted; if not, its read loop or session is down. "
                 "Check /gateway/agent/messages/unread?agent=CODE.")
    ok = _telegram("\n".join(lines))
    print(f"[dead-man] alerted Buck about {len(to_alert)} P0(s): telegram={'sent' if ok else 'FAILED'}")


if __name__ == "__main__":
    main()
