#!/usr/bin/env python3
"""
GBT Orchestrator — runs CA (Chief Architect) via the OpenAI Assistants API
instead of a chatgpt.com Custom GPT.

Why this exists: the ChatGPT Custom GPT product cannot self-trigger (Scheduled
Tasks drop Actions context), pins already-open chats to a stale tool schema
after any edit, throws a per-call confirmation prompt on write-type Actions,
and — confirmed 2026-07-16 — its tool-binding is unreliable even for
correctly-configured operations (ambGetUnread/agentQueueDashboard both
present and correct in the schema, both failed to bind as callable in three
separate fresh-chat tests, while the older getGatewayHealth worked fine).
This service owns the loop instead: it calls the Assistant via API, executes
every returned function call directly against the real MCP tool
implementations, submits results back, and posts CA's replies to the
message bus itself. No browser, no chat-version pinning, no confirmation
prompts, no unreliable binding.

One invocation = one poll-think-act cycle. Intended to run on a schedule
(cron/launchd, e.g. com.hci.gbt-orchestrator every 5-10 min), matching the
existing com.hci.api-server / com.hci.mcp-server launchd pattern — not a
long-running daemon, so it doesn't need its own crash/restart logic.

STATUS (2026-07-16): gather_new_work() is real and live-tested against the
actual gateway (Telegram, coordination bus, agent-queue) - it correctly
found and cleared a genuinely stale Telegram cursor on the 'chatgpt' agent
identity dating back to 2026-07-13 (content already handled via the
separately-tracked claude_code channel, so no work was lost). Everything
downstream of that (get_or_create_assistant/thread, run_assistant_turn) is
untested - no OPENAI_API_KEY exists yet. Buck needs to create an OpenAI
platform account (separate from ChatGPT Plus/Pro) and generate a key before
this can run end-to-end. See task #114.
"""
import json
import os
import ssl
import sys
import time
from pathlib import Path

import certifi
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(ROOT / ".env")

SSL_CTX = ssl.create_default_context(cafile=certifi.where())

sys.path.insert(0, str(ROOT / "03_Source_Code" / "services" / "mcp_server"))
sys.path.insert(0, str(ROOT / "03_Source_Code" / "api"))
sys.path.insert(0, str(ROOT / "03_Source_Code" / "integrations"))

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
STATE_FILE = Path(__file__).parent / "orchestrator_state.json"
TOOLS_FILE = Path(__file__).parent / "assistant_tools.json"
MODEL = os.environ.get("GBT_ASSISTANT_MODEL", "gpt-4.1")

GATEWAY_BASE = "https://speculate-armband-retinal.ngrok-free.dev"
API_KEY = "hci-a4fe3f56f42b981e59a98ec112c43ef975ac68c7fc0517c6"


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def get_or_create_assistant(client, state: dict):
    """Idempotent: reuse the stored assistant_id if it still exists, else create fresh."""
    assistant_id = state.get("assistant_id")
    if assistant_id:
        try:
            return client.beta.assistants.retrieve(assistant_id)
        except Exception:
            pass  # fall through to create

    instructions = (Path(__file__).parent / "instructions.md").read_text()
    tool_defs = json.loads(TOOLS_FILE.read_text())

    assistant = client.beta.assistants.create(
        name="HCI Chief Architect (CA)",
        instructions=instructions,
        model=MODEL,
        tools=tool_defs,
    )
    state["assistant_id"] = assistant.id
    save_state(state)
    return assistant


def get_or_create_thread(client, state: dict):
    thread_id = state.get("thread_id")
    if thread_id:
        try:
            return client.beta.threads.retrieve(thread_id)
        except Exception:
            pass

    thread = client.beta.threads.create()
    state["thread_id"] = thread.id
    save_state(state)
    return thread


def _gateway_get(path: str) -> dict:
    import urllib.request

    req = urllib.request.Request(
        f"{GATEWAY_BASE}{path}", headers={"X-API-Key": API_KEY}
    )
    with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as r:
        return json.loads(r.read())


def _gateway_post(path: str, body: dict) -> dict:
    import urllib.request

    req = urllib.request.Request(
        f"{GATEWAY_BASE}{path}",
        data=json.dumps(body).encode(),
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as r:
        return json.loads(r.read())


def gather_new_work() -> str | None:
    """
    Poll the same sources the standing coms-check loop checks: Telegram
    unread (agent='chatgpt', the existing identity in AI_HEARTBEAT_AGENTS —
    not renamed to 'ca', that's a separate Telegram-facing identity system,
    see gbt_gateway.py's _AGENT_ALIASES), coordination bus documents not yet
    acked by 'ca', and agent-queue pending tasks for 'ca'. Returns a
    plain-text prompt describing what's new, or None if nothing needs
    attention this cycle. Acks what it finds so the next cycle doesn't
    re-surface the same items (mirrors Claude Code's telegram/ack cursor
    pattern).
    """
    sections = []

    telegram = _gateway_get("/gateway/telegram/messages?agent=chatgpt")
    tg_messages = telegram.get("payload", {}).get("messages", [])
    if tg_messages:
        # 2026-07-16: was truncating to 300 chars - a real detailed ask from
        # CODE got cut off mid-sentence, contributing to CA giving shallow
        # "no actionable items" replies to what was actually a substantive
        # review request. Full message text now passed through; 300 chars
        # was never a real constraint, just an unexamined default.
        lines = [f"- {m['from']}: {m['text']}" for m in tg_messages]
        sections.append("UNREAD TELEGRAM MESSAGES:\n" + "\n".join(lines))
        last_id = max(m["message_id"] for m in tg_messages)
        _gateway_post("/gateway/telegram/ack", {"agent": "chatgpt", "message_id": last_id})

    coord = _gateway_get("/gateway/coordination/documents")
    docs = coord.get("payload", {}).get("documents", [])
    unacked = [d for d in docs if "ca" not in (d.get("acknowledged_by") or [])]
    if unacked:
        # 2026-07-16: was only ever passing the doc TITLE, never its content
        # or file_id - CA had no way to actually read what a document said,
        # so "process what's actionable" cycles were structurally incapable
        # of substantive review no matter how the doc was worded. Now
        # includes file_id and an explicit instruction to read it via
        # ReadDriveFile (a tool CA already has) before assessing.
        lines = [f"- \"{d['title']}\" (by {d.get('author', 'unknown')}, file_id={d['file_id']})"
                 for d in unacked]
        sections.append(
            "NEW COORDINATION BUS DOCUMENTS (call ReadDriveFile on each file_id "
            "below to see the actual content before deciding it's not actionable "
            "- the title alone is not enough to judge):\n" + "\n".join(lines)
        )
        for d in unacked:
            try:
                _gateway_post(
                    f"/gateway/coordination/documents/{d['file_id']}/acknowledge",
                    {"agent": "ca"},
                )
            except Exception:
                pass  # best-effort; don't let one bad doc block the whole cycle

    dash = _gateway_get("/gateway/agent-queue/ca/dashboard")
    pending = dash.get("payload", {}).get("queue_depth_by_status", {}).get("pending", 0)
    if pending:
        next_task = dash.get("payload", {}).get("next_scheduled_task", {})
        sections.append(
            f"QUEUE: {pending} pending task(s). Next: "
            f"{next_task.get('payload', {}).get('next_action', 'unknown')}"
        )

    if not sections:
        return None

    return (
        "Standing coms-check cycle. Here's what's new since last check:\n\n"
        + "\n\n".join(sections)
        + "\n\nProcess what's actionable. Report status in plain text — "
        "call SendAgentMessage directly for anything BC or CODE needs to see."
    )


def execute_tool_call(tool_call) -> str:
    """Dispatch a function call returned by the Assistant to the real MCP tool
    implementation and return a JSON string result."""
    import hci_mcp_server as tools

    name = tool_call.function.name
    try:
        args = json.loads(tool_call.function.arguments or "{}")
    except json.JSONDecodeError:
        return json.dumps({"error": f"invalid arguments JSON for {name}"})

    fn = getattr(tools, name, None)
    if fn is None:
        return json.dumps({"error": f"unknown tool: {name}"})

    try:
        result = fn(**args)
        return json.dumps(result) if not isinstance(result, str) else result
    except Exception as e:
        return json.dumps({"error": f"{name} raised: {e}"})


def run_assistant_turn(client, assistant, thread, prompt: str) -> str:
    """Send one prompt, drive the run to completion (handling tool calls),
    return the assistant's final plain-text reply."""
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=prompt
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant.id
    )

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action":
            tool_outputs = []
            for tc in run.required_action.submit_tool_outputs.tool_calls:
                output = execute_tool_call(tc)
                tool_outputs.append({"tool_call_id": tc.id, "output": output})
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
            )
            continue

        if run.status == "completed":
            messages = client.beta.threads.messages.list(
                thread_id=thread.id, order="desc", limit=1
            )
            reply = messages.data[0].content[0].text.value
            return reply

        if run.status in ("failed", "cancelled", "expired"):
            raise RuntimeError(f"Run ended with status={run.status}: {run.last_error}")

        time.sleep(1.5)


def post_to_message_bus(body: str, priority: str = "P2") -> None:
    """Mirrors what Claude Code does manually today when relaying CA's
    plain-text replies — the Assistants API version doesn't need the
    human-relay workaround since there's no per-call confirmation prompt, so
    this can be called directly as part of the same turn."""
    import urllib.request

    req = urllib.request.Request(
        f"{GATEWAY_BASE}/gateway/agent/messages",
        data=json.dumps({
            "from_agent": "CA",
            "to_agent": "ALL",
            "priority": priority,
            "subject": "CA update (via Assistants API orchestrator)",
            "body": body,
        }).encode(),
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15, context=SSL_CTX) as r:
        json.loads(r.read())


def main():
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY not set — nothing to do until Buck creates the "
              "OpenAI platform account and key (see task #114).", file=sys.stderr)
        sys.exit(1)

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    state = load_state()
    assistant = get_or_create_assistant(client, state)
    thread = get_or_create_thread(client, state)

    prompt = gather_new_work()
    if prompt is None:
        print("Nothing new for CA this cycle.")
        return

    reply = run_assistant_turn(client, assistant, thread, prompt)
    print(reply)
    post_to_message_bus(reply)


if __name__ == "__main__":
    main()
