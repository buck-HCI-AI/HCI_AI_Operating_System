"""
HCI AI — Microsoft Graph API client (Outlook / MS 365).
Account: buck@hendricksoninc.com
"""
import json, ssl, urllib.error, urllib.parse, urllib.request
import certifi
from credentials import get_ms_token

BASE    = "https://graph.microsoft.com/v1.0"
SSL_CTX = ssl.create_default_context(cafile=certifi.where())


def _token() -> str:
    return get_ms_token()


def _request(method: str, path: str, body: dict = None, params: dict = None):
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {_token()}")
    req.add_header("Accept", "application/json")
    if body:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as r:
            content = r.read()
            return json.loads(content) if content else {}, None
    except urllib.error.HTTPError as e:
        return None, f"{e.code}: {e.read().decode()[:300]}"


def list_inbox(top: int = 20, folder: str = "inbox") -> list[dict]:
    r, _ = _request("GET", f"/me/mailFolders/{folder}/messages", params={
        "$select": "id,subject,from,receivedDateTime,hasAttachments,isRead",
        "$top": top,
        "$orderby": "receivedDateTime desc",
    })
    return r.get("value", []) if r else []


def get_message(msg_id: str) -> dict:
    eid = urllib.parse.quote(msg_id, safe="")
    r, _ = _request("GET", f"/me/messages/{eid}")
    return r


def list_attachments(msg_id: str) -> list[dict]:
    eid = urllib.parse.quote(msg_id, safe="")
    r, _ = _request("GET", f"/me/messages/{eid}/attachments",
                    params={"$select": "id,name,contentType,size"})
    return r.get("value", []) if r else []


def download_attachment_bytes(msg_id: str, att_id: str) -> bytes:
    import base64
    eid = urllib.parse.quote(msg_id, safe="")
    aid = urllib.parse.quote(att_id, safe="")
    r, err = _request("GET", f"/me/messages/{eid}/attachments/{aid}")
    if err:
        raise RuntimeError(err)
    return base64.b64decode(r.get("contentBytes", ""))


def create_draft(subject: str, html_body: str, to: list[tuple[str, str]]) -> dict:
    """to: [(name, email), ...]"""
    msg = {
        "subject": subject,
        "body": {"contentType": "HTML", "content": html_body},
        "toRecipients": [{"emailAddress": {"name": n, "address": e}} for n, e in to],
        "isDraft": True,
    }
    r, err = _request("POST", "/me/messages", body=msg)
    if err:
        raise RuntimeError(err)
    return r


def patch_draft(msg_id: str, subject: str = None, html_body: str = None) -> dict:
    eid = urllib.parse.quote(msg_id, safe="")
    body = {}
    if subject:
        body["subject"] = subject
    if html_body:
        body["body"] = {"contentType": "HTML", "content": html_body}
    r, err = _request("PATCH", f"/me/messages/{eid}", body=body)
    if err:
        raise RuntimeError(err)
    return r


def get_unread_messages(top: int = 50) -> list[dict]:
    """All unread messages in inbox with full subject, sender, body preview."""
    r, _ = _request("GET", "/me/mailFolders/inbox/messages", params={
        "$select": "id,subject,from,receivedDateTime,hasAttachments,isRead,bodyPreview,conversationId",
        "$filter": "isRead eq false",
        "$top":    top,
        "$orderby": "receivedDateTime desc",
    })
    return r.get("value", []) if r else []


def delete_message(msg_id: str) -> tuple:
    """Permanently delete a message (moves to Deleted Items first, then hard deletes)."""
    eid = urllib.parse.quote(msg_id, safe="")
    return _request("DELETE", f"/me/messages/{eid}")


def move_message(msg_id: str, folder_id: str) -> tuple:
    """Move a message to a folder by folder ID."""
    eid = urllib.parse.quote(msg_id, safe="")
    return _request("POST", f"/me/messages/{eid}/move", body={"destinationId": folder_id})


def create_reply_draft(msg_id: str, html_body: str) -> dict:
    """Create a reply draft in the same email thread."""
    eid = urllib.parse.quote(msg_id, safe="")
    r, err = _request("POST", f"/me/messages/{eid}/createReply", body={
        "message": {"body": {"contentType": "HTML", "content": html_body}},
    })
    if err:
        raise RuntimeError(err)
    return r


def mark_as_read(msg_id: str) -> tuple:
    eid = urllib.parse.quote(msg_id, safe="")
    return _request("PATCH", f"/me/messages/{eid}", body={"isRead": True})


def send_email(subject: str, html_body: str, to: list[tuple[str, str]]) -> tuple:
    """LOCKED DOWN 2026-07-01 (incident: unauthorized live RFI emails to 101F/1355R
    design contacts, sent via this function with no approval gate — see ADR-010/011).
    This no longer calls /me/sendMail. It creates a draft instead and returns a result
    shaped like the old tuple so existing callers don't crash, but nothing is sent.
    Actual sending only happens via the approval-gated path in gbt_gateway.py
    (_send_approved_draft, triggered only by Buck's Telegram APPROVE)."""
    try:
        draft = create_draft(subject, html_body, to)
        return {"queued_draft_id": draft.get("id"), "status": "drafted_pending_approval",
                "note": "send_email() no longer sends live — draft created, requires Buck approval via gateway /email/send"}, None
    except Exception as e:
        return None, str(e)


def send_email_with_cc(subject: str, html_body: str, to: list[tuple[str, str]],
                       cc: list[tuple[str, str]] = None) -> tuple:
    """LOCKED DOWN 2026-07-01 — see send_email() above. Creates a draft only, never sends.
    CC recipients are noted in the draft body since Graph's createDraft (via /me/messages)
    honors ccRecipients directly if included in the message payload."""
    msg = {
        "subject": subject,
        "body": {"contentType": "HTML", "content": html_body},
        "toRecipients": [{"emailAddress": {"name": n, "address": e}} for n, e in to],
        "isDraft": True,
    }
    if cc:
        msg["ccRecipients"] = [{"emailAddress": {"name": n, "address": e}} for n, e in cc]
    r, err = _request("POST", "/me/messages", body=msg)
    if err:
        return None, err
    return {"queued_draft_id": r.get("id"), "status": "drafted_pending_approval",
            "note": "send_email_with_cc() no longer sends live — draft created, requires Buck approval via gateway /email/send"}, None


def send_draft(msg_id: str) -> tuple:
    """Send an existing Outlook draft by message ID."""
    return _request("POST", f"/me/messages/{msg_id}/send")


def list_drafts(top: int = 10) -> list[dict]:
    r, _ = _request("GET", "/me/mailFolders/drafts/messages", params={
        "$select": "id,subject,createdDateTime",
        "$top": top,
        "$orderby": "createdDateTime desc",
    })
    return r.get("value", []) if r else []
