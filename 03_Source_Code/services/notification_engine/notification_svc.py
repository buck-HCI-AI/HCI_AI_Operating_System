"""
Notification Engine — multi-provider dispatch with policy engine.

Providers: ntfy.sh (primary push), Pushover (backup push), Email (n8n), SMS (Twilio)
Policy: severity + context → provider selection

Mobile approvals: ntfy action buttons (Approve/Reject/Defer) hit the public ngrok URL.
Token auth bypasses API key on approve/reject/defer paths — token IS the auth.
"""
import os, json, logging
from typing import Optional
from datetime import datetime, timezone

import urllib.request

logger = logging.getLogger("hci.notifications")

POLICY = {
    "CRITICAL": ["ntfy", "pushover", "sms"],
    "HIGH":     ["ntfy", "email"],
    "MEDIUM":   ["email"],
    "LOW":      [],
}


def _public_url() -> str:
    return os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")


class NotificationService:

    @staticmethod
    def send(
        title: str,
        message: str,
        severity: str = "MEDIUM",
        tags: list[str] | None = None,
        action_url: str | None = None,
        topic: str | None = None,
        actions: list[dict] | None = None,
    ) -> dict:
        providers = POLICY.get(severity.upper(), ["email"])
        results = {}
        for provider in providers:
            try:
                if provider == "ntfy":
                    results["ntfy"] = _send_ntfy(title, message, tags or [], action_url, topic, actions)
                elif provider == "pushover":
                    results["pushover"] = _send_pushover(title, message, action_url)
                elif provider == "email":
                    results["email"] = _queue_email(title, message, action_url)
                elif provider == "sms":
                    results["sms"] = _send_sms(title + ": " + message)
            except Exception as e:
                logger.error("Notification provider %s failed: %s", provider, e)
                results[provider] = {"status": "error", "error": str(e)}

        return {
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "severity": severity,
            "providers_attempted": providers,
            "results": results,
        }

    @staticmethod
    def approval_required(
        exec_id: str,
        title: str,
        approve_token: str,
        reject_token: str,
        defer_token: str,
        deadline: str | None = None,
        confidence: str = "High",
    ) -> dict:
        """Actionable approval notification with Approve/Reject/Defer buttons."""
        base = _public_url()
        approve_url = f"{base}/api/v1/executive/approve/{exec_id}?token={approve_token}"
        reject_url  = f"{base}/api/v1/executive/reject/{exec_id}?token={reject_token}"
        defer_url   = f"{base}/api/v1/executive/defer/{exec_id}?token={defer_token}"
        dash_url    = f"{base}/executive"

        deadline_str = f" · Due {deadline}" if deadline else ""
        message = f"{title}{deadline_str}\nConfidence: {confidence}"

        # view actions open Safari → GET request → server returns confirmation page
        # This gives visible feedback vs. silent http POST with no response shown
        actions = [
            {"action": "view", "label": "Approve",   "url": approve_url},
            {"action": "view", "label": "Defer",     "url": defer_url},
            {"action": "view", "label": "Dashboard", "url": dash_url},
        ]

        return NotificationService.send(
            title=f"Decision Required: {exec_id}",
            message=message,
            severity="HIGH",
            tags=["rotating_light", "construction"],
            action_url=approve_url,
            actions=actions,
        )

    @staticmethod
    def alert_critical_inbox(exec_id: str, title: str, approve_url: str) -> dict:
        base = _public_url()
        return NotificationService.send(
            title=f"OVERDUE: {exec_id}",
            message=title,
            severity="CRITICAL",
            tags=["rotating_light", "clock3"],
            action_url=approve_url,
            actions=[
                {"action": "view", "label": "Approve Now", "url": approve_url},
                {"action": "view", "label": "Dashboard",   "url": f"{base}/executive"},
            ],
        )

    @staticmethod
    def alert_system_down(service: str) -> dict:
        return NotificationService.send(
            title=f"HCI AI — {service} DOWN",
            message=f"Service {service} is not responding. Check logs.",
            severity="CRITICAL",
            tags=["warning", "no_entry"],
        )

    @staticmethod
    def morning_brief_push(
        inbox_count: int,
        health: str,
        one_action: Optional[str],
        top_exec_id: str | None = None,
        approve_token: str | None = None,
        reject_token: str | None = None,
        defer_token: str | None = None,
    ) -> dict:
        base = _public_url()
        msg = f"{health} · {inbox_count} decision{'s' if inbox_count != 1 else ''} pending"
        if one_action:
            msg += f"\n{one_action}"

        actions = []
        if top_exec_id and approve_token:
            actions = [
                {"action": "view", "label": "Approve",   "url": f"{base}/api/v1/executive/approve/{top_exec_id}?token={approve_token}"},
                {"action": "view", "label": "Defer",     "url": f"{base}/api/v1/executive/defer/{top_exec_id}?token={defer_token}"},
                {"action": "view", "label": "Dashboard", "url": f"{base}/executive"},
            ]
        else:
            actions = [{"action": "view", "label": "Open Dashboard", "url": f"{base}/executive"}]

        return NotificationService.send(
            title="HCI AI Morning Brief",
            message=msg,
            severity="HIGH",
            tags=["sun_with_face", "construction"],
            actions=actions,
        )


# ── Provider Adapters ──────────────────────────────────────────────────────────

def _send_ntfy(
    title: str,
    message: str,
    tags: list,
    action_url: str | None,
    topic: str | None,
    actions: list[dict] | None = None,
) -> dict:
    import ssl, certifi
    ctx = ssl.create_default_context(cafile=certifi.where())

    ntfy_url   = os.environ.get("NTFY_URL",   "https://ntfy.sh")
    ntfy_topic = topic or os.environ.get("NTFY_TOPIC", "hci-executive")
    ntfy_token = os.environ.get("NTFY_TOKEN", "")

    # ntfy headers must be ASCII — strip unicode
    safe_title = title.encode("ascii", "replace").decode("ascii")

    headers = {
        "Title":        safe_title,
        "Content-Type": "text/plain; charset=utf-8",
        # Explicit retention: ensures messages appear in app history even if the
        # app's WebSocket was disconnected when delivery occurred. Without this,
        # re-subscribed topics with in-app caching toggled off show empty history.
        "Cache":        "yes",
        "Expires":      "24h",
    }
    if tags:
        headers["Tags"] = ",".join(tags)
    if action_url and not actions:
        # Simple click-through when no action buttons
        headers["Click"] = action_url
    if ntfy_token:
        headers["Authorization"] = f"Bearer {ntfy_token}"

    # Build action buttons string
    # Format: "http, Label, URL, method=POST, clear=true; view, Label, URL"
    if actions:
        parts = []
        for a in actions:
            atype = a.get("action", "view")
            label = a.get("label", "Open")
            url   = a.get("url", "")
            if atype == "http":
                method = a.get("method", "POST")
                clear  = "true" if a.get("clear") else "false"
                parts.append(f"http, {label}, {url}, method={method}, clear={clear}")
            else:
                parts.append(f"view, {label}, {url}")
        headers["Actions"] = "; ".join(parts)

    req = urllib.request.Request(
        f"{ntfy_url}/{ntfy_topic}",
        data=message.encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5, context=ctx) as r:
        return {"status": "sent", "http_status": r.status, "topic": ntfy_topic, "actions": len(actions or [])}


def _send_pushover(title: str, message: str, action_url: str | None = None) -> dict:
    import ssl, certifi
    ctx = ssl.create_default_context(cafile=certifi.where())

    token    = os.environ.get("PUSHOVER_TOKEN", "")
    user_key = os.environ.get("PUSHOVER_USER_KEY", "")
    if not token or not user_key:
        return {"status": "skipped", "reason": "PUSHOVER_TOKEN or PUSHOVER_USER_KEY not configured"}

    data = {"token": token, "user": user_key, "title": title, "message": message}
    if action_url:
        data["url"] = action_url
        data["url_title"] = "Open"

    payload = json.dumps(data).encode()
    req = urllib.request.Request(
        "https://api.pushover.net/1/messages.json",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5, context=ctx) as r:
        return {"status": "sent", "http_status": r.status}


def _queue_email(title: str, message: str, action_url: str | None) -> dict:
    import ssl, certifi
    ctx = ssl.create_default_context(cafile=certifi.where())

    n8n_webhook = os.environ.get("N8N_EMAIL_WEBHOOK", "")
    if not n8n_webhook:
        return {"status": "skipped", "reason": "N8N_EMAIL_WEBHOOK not configured"}
    payload = json.dumps({
        "subject": title,
        "body": message,
        "action_url": action_url,
        "to": os.environ.get("EXECUTIVE_EMAIL", "buck@ahmaspen.com"),
    }).encode()
    req = urllib.request.Request(
        n8n_webhook, data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=5, context=ctx) as r:
        return {"status": "queued", "http_status": r.status}


def _send_sms(message: str) -> dict:
    import ssl, certifi, base64
    ctx = ssl.create_default_context(cafile=certifi.where())

    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token  = os.environ.get("TWILIO_AUTH_TOKEN", "")
    from_number = os.environ.get("TWILIO_FROM", "")
    to_number   = os.environ.get("EXECUTIVE_PHONE", "")
    if not all([account_sid, auth_token, from_number, to_number]):
        return {"status": "skipped", "reason": "Twilio credentials not configured"}

    payload = f"From={urllib.request.quote(from_number)}&To={urllib.request.quote(to_number)}&Body={urllib.request.quote(message[:160])}".encode()
    credentials = base64.b64encode(f"{account_sid}:{auth_token}".encode()).decode()
    req = urllib.request.Request(
        f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
        data=payload,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5, context=ctx) as r:
        return {"status": "sent", "http_status": r.status}
