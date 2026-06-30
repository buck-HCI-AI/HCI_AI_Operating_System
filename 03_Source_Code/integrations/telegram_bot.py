"""
HCI AI — Telegram Bot integration.
Bot: @hciaiossystem_bot  |  Owner chat: TELEGRAM_CHAT_ID
Send notifications, approval buttons, and receive Buck's replies.
"""
import json, os, ssl, urllib.error, urllib.parse, urllib.request
import certifi

TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
BASE    = f"https://api.telegram.org/bot{TOKEN}"
SSL_CTX = ssl.create_default_context(cafile=certifi.where())


def _post(endpoint: str, payload: dict) -> tuple[dict, str | None]:
    url  = f"{BASE}/{endpoint}"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return {}, f"{e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return {}, str(e)


def send_message(text: str, chat_id: str = None, parse_mode: str = "Markdown",
                 reply_markup: dict = None) -> tuple[dict, str | None]:
    """Send a plain text message to Buck."""
    payload = {
        "chat_id":    chat_id or CHAT_ID,
        "text":       text,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return _post("sendMessage", payload)


def send_approval(title: str, body: str, approve_url: str, reject_url: str = None,
                  defer_url: str = None, chat_id: str = None) -> tuple[dict, str | None]:
    """Send a message with Approve / Reject / Defer inline buttons."""
    buttons = [[{"text": "✅ Approve", "url": approve_url}]]
    if reject_url:
        buttons[0].append({"text": "❌ Reject", "url": reject_url})
    if defer_url:
        buttons[0].append({"text": "⏸ Defer", "url": defer_url})
    markup = {"inline_keyboard": buttons}
    text = f"*{title}*\n\n{body}"
    return send_message(text, chat_id=chat_id, reply_markup=markup)


def send_alert(title: str, body: str, priority: str = "normal") -> tuple[dict, str | None]:
    """Send a formatted alert. priority: low | normal | high | urgent"""
    icons = {"low": "ℹ️", "normal": "📋", "high": "⚠️", "urgent": "🚨"}
    icon = icons.get(priority, "📋")
    text = f"{icon} *{title}*\n\n{body}"
    return send_message(text)


def get_updates(offset: int = None, limit: int = 20) -> tuple[list, str | None]:
    """Poll for new messages from Buck."""
    payload = {"limit": limit, "timeout": 0}
    if offset is not None:
        payload["offset"] = offset
    data, err = _post("getUpdates", payload)
    if err:
        return [], err
    return data.get("result", []), None


def set_webhook(url: str) -> tuple[dict, str | None]:
    """Register the ngrok webhook so Telegram pushes updates instead of polling."""
    return _post("setWebhook", {"url": url, "allowed_updates": ["message", "callback_query"]})


def delete_webhook() -> tuple[dict, str | None]:
    return _post("deleteWebhook", {})


def answer_callback(callback_query_id: str, text: str = "") -> tuple[dict, str | None]:
    """Acknowledge an inline button tap."""
    return _post("answerCallbackQuery", {"callback_query_id": callback_query_id, "text": text})
