"""
Notification Engine — multi-provider dispatch with policy engine.

Providers: ntfy.sh (primary push), Pushover (backup push), Email (n8n), SMS (Twilio)
Policy: severity + context → provider selection
"""
import os, json, logging
from typing import Optional
from datetime import datetime, timezone

import urllib.request

logger = logging.getLogger("hci.notifications")

# ── Policy Engine ──────────────────────────────────────────────────────────────
# severity → providers to use (in order)
POLICY = {
    "CRITICAL": ["ntfy", "pushover", "sms"],
    "HIGH":     ["ntfy", "email"],
    "MEDIUM":   ["email"],
    "LOW":      [],  # weekly digest only — n8n collects and batches
}


class NotificationService:

    @staticmethod
    def send(
        title: str,
        message: str,
        severity: str = "MEDIUM",
        tags: list[str] | None = None,
        action_url: str | None = None,
        topic: str | None = None,
    ) -> dict:
        providers = POLICY.get(severity.upper(), ["email"])
        results = {}
        for provider in providers:
            try:
                if provider == "ntfy":
                    results["ntfy"] = _send_ntfy(title, message, tags or [], action_url, topic)
                elif provider == "pushover":
                    results["pushover"] = _send_pushover(title, message)
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
    def alert_critical_inbox(exec_id: str, title: str, approve_url: str) -> dict:
        return NotificationService.send(
            title=f"ACTION REQUIRED: {exec_id}",
            message=title,
            severity="HIGH",
            tags=["rotating_light", "construction"],
            action_url=approve_url,
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
    def morning_brief_push(inbox_count: int, health: str, one_action: Optional[str]) -> dict:
        msg = f"{health} · {inbox_count} decisions pending"
        if one_action:
            msg += f" · {one_action}"
        return NotificationService.send(
            title="HCI AI Morning Brief",
            message=msg,
            severity="HIGH",
            tags=["sun_with_face", "construction"],
        )


# ── Provider Adapters ──────────────────────────────────────────────────────────

def _send_ntfy(title: str, message: str, tags: list, action_url: str | None, topic: str | None) -> dict:
    ntfy_url = os.environ.get("NTFY_URL", "https://ntfy.sh")
    ntfy_topic = topic or os.environ.get("NTFY_TOPIC", "hci-executive")
    ntfy_token = os.environ.get("NTFY_TOKEN", "")

    headers = {
        "Title": title,
        "Content-Type": "text/plain",
    }
    if tags:
        headers["Tags"] = ",".join(tags)
    if action_url:
        headers["Click"] = action_url
    if ntfy_token:
        headers["Authorization"] = f"Bearer {ntfy_token}"

    req = urllib.request.Request(
        f"{ntfy_url}/{ntfy_topic}",
        data=message.encode(),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        return {"status": "sent", "http_status": r.status, "topic": ntfy_topic}


def _send_pushover(title: str, message: str) -> dict:
    token = os.environ.get("PUSHOVER_TOKEN", "")
    user_key = os.environ.get("PUSHOVER_USER_KEY", "")
    if not token or not user_key:
        return {"status": "skipped", "reason": "PUSHOVER_TOKEN or PUSHOVER_USER_KEY not configured"}

    payload = json.dumps({
        "token": token,
        "user": user_key,
        "title": title,
        "message": message,
    }).encode()
    req = urllib.request.Request(
        "https://api.pushover.net/1/messages.json",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        return {"status": "sent", "http_status": r.status}


def _queue_email(title: str, message: str, action_url: str | None) -> dict:
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
    with urllib.request.urlopen(req, timeout=5) as r:
        return {"status": "queued", "http_status": r.status}


def _send_sms(message: str) -> dict:
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    from_number = os.environ.get("TWILIO_FROM", "")
    to_number = os.environ.get("EXECUTIVE_PHONE", "")
    if not all([account_sid, auth_token, from_number, to_number]):
        return {"status": "skipped", "reason": "Twilio credentials not configured"}

    import base64
    payload = f"From={from_number}&To={to_number}&Body={urllib.request.quote(message[:160])}".encode()
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
    with urllib.request.urlopen(req, timeout=5) as r:
        return {"status": "sent", "http_status": r.status}
