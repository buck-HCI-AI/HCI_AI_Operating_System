"""
WF-006: Inbox Review
Runs every morning after bid leveling:
  1. Reads all unread Outlook emails
  2. Classifies each by project (keyword matching)
  3. Moves to correct inbox subfolder
  4. Drafts an AI reply in the same thread (using Claude)
  5. Returns structured summary for morning brief

Requires ANTHROPIC_API_KEY in .env for AI drafts.
Falls back to template drafts if key not set.
"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from microsoft_graph import get_unread_messages, move_message, create_reply_draft, mark_as_read

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Folder routing ─────────────────────────────────────────────────────────────

FOLDERS = {
    "64 Eastwood":    os.environ.get("FOLDER_64_EASTWOOD",    ""),
    "101 Francis":    os.environ.get("FOLDER_101_FRANCIS",    ""),
    "1355 Riverside": os.environ.get("FOLDER_1355_RIVERSIDE", ""),
    "83 Sagebrusch":  os.environ.get("FOLDER_83_SAGEBRUSCH",  ""),
    "HCI Admin":      os.environ.get("FOLDER_HCI_ADMIN",      ""),
}

# Keywords that map to each project folder
ROUTING_RULES = [
    ("64 Eastwood",    ["64 eastwood", "eastwood"]),
    ("101 Francis",    ["101 francis", "francis"]),
    ("1355 Riverside", ["1355 riverside", "riverside"]),
    ("83 Sagebrusch",  ["83 sagebrusch", "sagebrusch"]),
]


def classify_email(subject: str, preview: str, sender: str) -> str:
    """Return the folder name this email belongs to."""
    text = f"{subject} {preview} {sender}".lower()
    for folder_name, keywords in ROUTING_RULES:
        for kw in keywords:
            if kw in text:
                return folder_name
    return "HCI Admin"


# ── AI draft generation ────────────────────────────────────────────────────────

DRAFT_SYSTEM_PROMPT = """You are drafting email replies on behalf of Buck Adams,
owner of Hendrickson Construction (HCI), a high-end residential remodeling company in Aspen, CO.

Write professional, concise replies. Buck's tone is direct and friendly.
Keep drafts under 100 words unless the email requires a detailed response.
Do not make commitments about pricing, timelines, or awards without Buck's approval.
Sign off as: Buck Adams | Hendrickson Construction | buck@hendricksoninc.com"""


def draft_reply(subject: str, sender_name: str, body_preview: str, project: str) -> str:
    """Generate an AI draft reply. Falls back to template if no API key."""
    if not ANTHROPIC_API_KEY:
        return _template_draft(sender_name, subject, project)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=DRAFT_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": (
                    f"Draft a reply to this email.\n\n"
                    f"Project: {project}\n"
                    f"From: {sender_name}\n"
                    f"Subject: {subject}\n"
                    f"Email preview: {body_preview[:500]}\n\n"
                    f"Write only the email body text, no subject line."
                )
            }]
        )
        return msg.content[0].text
    except Exception as e:
        return _template_draft(sender_name, subject, project) + f"\n\n[AI draft failed: {e}]"


def _template_draft(sender_name: str, subject: str, project: str) -> str:
    first_name = sender_name.split()[0] if sender_name else "there"
    proj_note  = f" regarding {project}" if project != "HCI Admin" else ""
    return (
        f"Hi {first_name},\n\n"
        f"Thank you for your email{proj_note}. I've received your message and will "
        f"review and follow up with you shortly.\n\n"
        f"Best,\nBuck Adams\nHendrickson Construction\nbuck@hendricksoninc.com"
    )


def _to_html(text: str) -> str:
    lines = text.replace("\r", "").split("\n")
    return "<br>".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────

def run(max_emails: int = 30, create_drafts: bool = True) -> dict:
    """
    Process all unread inbox emails.
    Returns structured summary for inclusion in morning brief.
    """
    print("\n=== Inbox Review (WF-006) ===")
    result = {
        "total_unread": 0,
        "processed":    0,
        "by_project":   {},
        "emails":       [],
        "errors":       [],
    }

    messages = get_unread_messages(top=max_emails)
    result["total_unread"] = len(messages)
    print(f"  Found {len(messages)} unread messages")

    for msg in messages:
        try:
            msg_id    = msg["id"]
            subject   = msg.get("subject", "(no subject)")
            preview   = msg.get("bodyPreview", "")
            sender    = (msg.get("from") or {}).get("emailAddress", {})
            sender_name  = sender.get("name", "")
            sender_email = sender.get("address", "")
            received  = msg.get("receivedDateTime", "")

            # 1 — Classify
            project = classify_email(subject, preview, sender_email)

            # 2 — Draft reply FIRST (before move — message ID changes after move)
            draft_id = None
            if create_drafts and sender_email and "noreply" not in sender_email.lower() and "notifications@" not in sender_email.lower():
                draft_text = draft_reply(subject, sender_name, preview, project)
                draft_html = _to_html(draft_text)
                try:
                    draft = create_reply_draft(msg_id, draft_html)
                    draft_id = draft.get("id")
                except Exception as e:
                    result["errors"].append(f"Draft failed ({subject[:40]}): {e}")

            # 3 — Move to folder AFTER drafting
            folder_id = FOLDERS.get(project)
            moved = False
            if folder_id:
                _, err = move_message(msg_id, folder_id)
                moved = err is None
                if err:
                    result["errors"].append(f"Move failed ({subject[:40]}): {err}")

            # 4 — Track
            entry = {
                "subject":      subject,
                "from_name":    sender_name,
                "from_email":   sender_email,
                "received":     received,
                "project":      project,
                "moved":        moved,
                "draft_created": draft_id is not None,
            }
            result["emails"].append(entry)
            result["by_project"].setdefault(project, []).append(entry)
            result["processed"] += 1

            print(f"  ✓ [{project}] {subject[:50]} — moved={moved}, draft={draft_id is not None}")

        except Exception as e:
            result["errors"].append(f"Email {msg.get('id','?')}: {e}")

    result["status"] = "success" if not result["errors"] else "partial"
    print(f"  ✓ Inbox review done — {result['processed']} processed, {len(result['errors'])} errors")
    return result
