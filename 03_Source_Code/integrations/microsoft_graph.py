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


def send_email(subject: str, html_body: str, to: list[tuple[str, str]]) -> tuple:
    """Send immediately via /me/sendMail. to: [(name, email), ...]"""
    msg = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html_body},
            "toRecipients": [{"emailAddress": {"name": n, "address": e}} for n, e in to],
        },
        "saveToSentItems": True,
    }
    return _request("POST", "/me/sendMail", body=msg)


def list_drafts(top: int = 10) -> list[dict]:
    r, _ = _request("GET", "/me/mailFolders/drafts/messages", params={
        "$select": "id,subject,createdDateTime",
        "$top": top,
        "$orderby": "createdDateTime desc",
    })
    return r.get("value", []) if r else []
