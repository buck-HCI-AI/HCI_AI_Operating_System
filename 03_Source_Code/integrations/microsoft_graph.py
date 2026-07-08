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


def create_draft(subject: str, html_body: str, to: list[tuple[str, str]],
                  cc: list[tuple[str, str]] = None) -> dict:
    """to: [(name, email), ...]"""
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


# History: self-send bypass existed pre-2026-07-01, got removed 2026-07-07 after it
# was found auto-sending self-addressed reports (morning brief etc.) with zero review
# step - the same failure mode the "never auto-send" rule was written to prevent for
# EXTERNAL mail. That fix over-corrected: it drafted everything, including pure
# informational reports addressed only to Buck himself. Buck's own clarification
# 2026-07-08: reports should land in his Inbox directly; the draft-and-approve gate is
# for POTENTIAL OUTGOING mail (anything an external party would see), not for a report
# only he reads. The risk profiles are genuinely different - a self-addressed report
# landing in Inbox instead of Drafts is not an irreversible external commitment, it's
# the exact same content in a different folder of his own mailbox.
#
# So: send_email() now sends directly (Inbox, via /me/sendMail) ONLY when every
# recipient's address is exactly Buck's own - checked here, not left to the caller.
# ANY external recipient anywhere (to, or cc via send_email_with_cc) still drafts,
# unconditionally, same as before. This is not a return to the old allowlist pattern -
# it's a strict address-equality check run on every call, not a name-based carve-out.
BUCK_SELF_ADDRESS = "buck@hendricksoninc.com"


def _all_recipients_self(to: list[tuple[str, str]], cc: list[tuple[str, str]] = None) -> bool:
    addrs = [e.lower() for _, e in to] + [e.lower() for _, e in (cc or [])]
    return bool(addrs) and all(a == BUCK_SELF_ADDRESS for a in addrs)


def _send_direct(subject: str, html_body: str, to: list[tuple[str, str]]) -> dict:
    """Real send via /me/sendMail - only ever called after _all_recipients_self()
    confirms every recipient is Buck's own address. Lands in his Inbox."""
    msg = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [{"emailAddress": {"name": n, "address": e}} for n, e in to],
        },
        "saveToSentItems": True,
    }
    r, err = _request("POST", "/me/sendMail", body=msg)
    if err:
        raise RuntimeError(err)
    return {"status": "sent_to_inbox"}


def send_email(subject: str, html_body: str, to: list[tuple[str, str]]) -> tuple:
    """Self-addressed (report) mail sends directly to Inbox. Any external recipient
    always drafts and requires Buck's approval via gateway /email/send. See note above."""
    try:
        if _all_recipients_self(to):
            result = _send_direct(subject, html_body, to)
            return result, None
        draft = create_draft(subject, html_body, to)
        return {"queued_draft_id": draft.get("id"), "status": "drafted_pending_approval",
                "note": "Draft created - requires Buck approval via gateway /email/send"}, None
    except Exception as e:
        return None, str(e)


def send_email_with_cc(subject: str, html_body: str, to: list[tuple[str, str]],
                       cc: list[tuple[str, str]] = None) -> tuple:
    """Same self-address check as send_email() - drafts unless every to/cc recipient
    is Buck's own address, in which case it sends directly to his Inbox."""
    if _all_recipients_self(to, cc):
        try:
            return _send_direct(subject, html_body, to), None
        except Exception as e:
            return None, str(e)
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
