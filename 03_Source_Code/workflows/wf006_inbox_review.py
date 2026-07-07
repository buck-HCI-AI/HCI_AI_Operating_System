"""
WF-006: Inbox Review
Runs every morning:
  1. Reads all unread Outlook emails
  2. Classifies each by project (keyword matching)
  3. Detects bid emails → writes to bid_entries (Phase 9.4)
  4. Detects RFI/submittal emails → writes to rfis/submittals (Phase 9.5)
  5. Moves to correct inbox subfolder
  6. Drafts an AI reply in the same thread (using Claude)
  7. Returns structured summary for morning brief

Requires ANTHROPIC_API_KEY in .env for AI drafts.
Falls back to template drafts if key not set.
"""
import sys, os, re, json, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "integrations"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from microsoft_graph import get_unread_messages, move_message, create_reply_draft, mark_as_read

import psycopg2, psycopg2.extras

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

DB = dict(
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    dbname=os.environ.get("POSTGRES_DB", "hci_os"),
    user=os.environ.get("POSTGRES_USER", "hci_admin"),
    password=os.environ.get("POSTGRES_PASSWORD", ""),
)

# ── Folder routing ─────────────────────────────────────────────────────────────

FOLDERS = {
    "64 Eastwood":    os.environ.get("FOLDER_64_EASTWOOD",    ""),
    "101 Francis":    os.environ.get("FOLDER_101_FRANCIS",    ""),
    "1355 Riverside": os.environ.get("FOLDER_1355_RIVERSIDE", ""),
    "83 Sagebrusch":  os.environ.get("FOLDER_83_SAGEBRUSCH",  ""),
    "HCI Admin":      os.environ.get("FOLDER_HCI_ADMIN",      ""),
}

PROJECT_NUMBERS = {
    "64 Eastwood":    "64EW",
    "101 Francis":    "101F",
    "1355 Riverside": "1355R",
    "83 Sagebrusch":  "83S",
}

ROUTING_RULES = [
    ("64 Eastwood",    ["64 eastwood", "eastwood"]),
    ("101 Francis",    ["101 francis", "francis"]),
    ("1355 Riverside", ["1355 riverside", "riverside"]),
    ("83 Sagebrusch",  ["83 sagebrusch", "sagebrusch"]),
]

# Bid detection keywords
BID_KEYWORDS = [
    "bid", "quote", "quotation", "proposal", "estimate", "pricing",
    "unit price", "lump sum", "scope of work", "per plan", "per spec",
]
# RFI detection keywords
RFI_KEYWORDS = [
    "rfi", "request for information", "clarification", "rfp clarification",
    "field question", "plan question",
]
# Submittal detection keywords
SUBMITTAL_KEYWORDS = [
    "submittal", "shop drawing", "product data", "material approval",
    "cut sheet", "sample", "mock-up", "operation & maintenance",
]

# Fixed 2026-07-07: the old check (`"noreply" not in sender` and `"notifications@" not
# in sender`) was a single literal substring each way, so it missed every real-world
# variant - found live via Buck's Drafts folder full of AI-drafted "replies" to
# no-reply@accounts.google.com (hyphenated), quickbooks@notification.intuit.com
# (singular, no @), reply@ngrok.com, onboarding@hubspot.com, team@perplexity.ai, and
# noreply@grammarly.com piling up daily since at least 06-30. This is drafts-only (no
# send risk after the separate microsoft_graph.py fix), but it was wasting Claude API
# calls drafting replies to spam/notification/marketing mail nobody should ever reply
# to. Broadened to a regex covering the common no-reply/transactional local-part
# patterns, plus a blocklist of the specific SaaS-notification domains actually seen
# sending to this inbox - not exhaustive, but covers everything observed so far.
_NO_REPLY_PATTERN = re.compile(
    r"no.?reply|do.?not.?reply|donotreply|notifications?@|mailer.?daemon|"
    r"auto.?reply|autoresponder|no\.reply|bounce",
    re.IGNORECASE,
)
_TRANSACTIONAL_DOMAINS = {
    "grammarly.com", "accounts.google.com", "hubspot.com", "ngrok.com",
    "notification.intuit.com", "perplexity.ai", "openweathermap.org",
}


def _is_automated_sender(sender_email: str) -> bool:
    if not sender_email:
        return True
    email = sender_email.lower()
    if _NO_REPLY_PATTERN.search(email):
        return True
    domain = email.split("@")[-1]
    return any(domain == d or domain.endswith("." + d) for d in _TRANSACTIONAL_DOMAINS)


def classify_email(subject: str, preview: str, sender: str) -> str:
    text = f"{subject} {preview} {sender}".lower()
    for folder_name, keywords in ROUTING_RULES:
        for kw in keywords:
            if kw in text:
                return folder_name
    return "HCI Admin"


# ── Bid detection (Phase 9.4) ──────────────────────────────────────────────────

def _extract_dollar_amount(text: str):
    """Extract largest dollar amount from text. Returns float or None."""
    amounts = re.findall(r'\$\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})?)', text)
    if not amounts:
        return None
    parsed = []
    for a in amounts:
        try:
            parsed.append(float(a.replace(",", "")))
        except ValueError:
            pass
    return max(parsed) if parsed else None


def _is_bid_email(subject: str, preview: str) -> bool:
    text = f"{subject} {preview}".lower()
    return any(kw in text for kw in BID_KEYWORDS)


def _match_vendor(sender_name: str, sender_email: str, conn) -> int | None:
    """Try to match sender to a vendor in the vendors table."""
    cur = conn.cursor()
    # Match by email domain first
    domain = sender_email.split("@")[-1].lower() if "@" in sender_email else ""
    if domain:
        cur.execute(
            "SELECT id FROM vendors WHERE LOWER(email) LIKE %s LIMIT 1",
            (f"%@{domain}",)
        )
        row = cur.fetchone()
        if row:
            return row["id"]
    # Match by company name tokens
    tokens = [w for w in re.sub(r'[^\w\s]', ' ', sender_name.lower()).split()
              if len(w) > 3 and w not in {'inc', 'llc', 'corp', 'the', 'and'}]
    for token in tokens[:3]:
        cur.execute(
            "SELECT id FROM vendors WHERE LOWER(company_name) LIKE %s LIMIT 1",
            (f"%{token}%",)
        )
        row = cur.fetchone()
        if row:
            return row["id"]
    return None


def _resolve_project_id(project_folder: str, conn) -> int | None:
    if project_folder == "HCI Admin":
        return None
    project_number = PROJECT_NUMBERS.get(project_folder)
    if not project_number:
        return None
    cur = conn.cursor()
    prefix = re.match(r'^(\d+)', project_number)
    if not prefix:
        return None
    cur.execute(
        "SELECT id FROM projects WHERE name ILIKE %s OR address ILIKE %s LIMIT 1",
        (f"{prefix.group(1)}%", f"{prefix.group(1)}%")
    )
    row = cur.fetchone()
    return row["id"] if row else None


def _write_bid_entry(subject, sender_name, sender_email, preview, project_folder,
                     amount, msg_id, conn) -> bool:
    """Write a detected bid to bid_entries. Returns True if written."""
    project_id = _resolve_project_id(project_folder, conn)
    if not project_id:
        return False
    vendor_id = _match_vendor(sender_name, sender_email, conn)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bid_entries (project_id, vendor_id, bid_amount, status, notes, source, date_received)
        VALUES (%s, %s, %s, 'received', %s, 'email', CURRENT_DATE)
        ON CONFLICT DO NOTHING
    """, (
        project_id, vendor_id, amount,
        f"Subject: {subject[:200]}\nFrom: {sender_name} <{sender_email}>\nPreview: {preview[:300]}"
    ))
    conn.commit()
    return True


# ── RFI / Submittal detection (Phase 9.5) ─────────────────────────────────────

def _is_rfi_email(subject: str, preview: str) -> bool:
    text = f"{subject} {preview}".lower()
    return any(kw in text for kw in RFI_KEYWORDS)


def _is_submittal_email(subject: str, preview: str) -> bool:
    text = f"{subject} {preview}".lower()
    return any(kw in text for kw in SUBMITTAL_KEYWORDS)


def _write_rfi(subject, sender_name, preview, project_folder, msg_id, conn) -> bool:
    project_id = _resolve_project_id(project_folder, conn)
    if not project_id:
        return False
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(MAX(CAST(NULLIF(REGEXP_REPLACE(rfi_number,'[^0-9]','','g'),'') AS INTEGER)),0)+1 "
        "FROM rfis WHERE project_id = %s", (project_id,)
    )
    next_num = (cur.fetchone()[0] or 1)
    rfi_number = f"RFI-{next_num:03d}"
    cur.execute("""
        INSERT INTO rfis (project_id, rfi_number, subject, submitted_by, question,
                          submitted_date, source_email_id)
        VALUES (%s, %s, %s, %s, %s, CURRENT_DATE, %s)
    """, (project_id, rfi_number, subject[:500], sender_name, preview[:2000], msg_id))
    conn.commit()
    return True


def _write_submittal(subject, sender_name, preview, project_folder, msg_id, conn) -> bool:
    project_id = _resolve_project_id(project_folder, conn)
    if not project_id:
        return False
    cur = conn.cursor()
    cur.execute(
        "SELECT COALESCE(MAX(CAST(NULLIF(REGEXP_REPLACE(submittal_number,'[^0-9]','','g'),'') AS INTEGER)),0)+1 "
        "FROM submittals WHERE project_id = %s", (project_id,)
    )
    next_num = (cur.fetchone()[0] or 1)
    submittal_number = f"SUB-{next_num:03d}"
    cur.execute("""
        INSERT INTO submittals (project_id, submittal_number, description, submitted_by,
                                submitted_date, source_email_id)
        VALUES (%s, %s, %s, %s, CURRENT_DATE, %s)
    """, (project_id, submittal_number, subject[:500], sender_name, msg_id))
    conn.commit()
    return True


# ── AI draft generation ────────────────────────────────────────────────────────

DRAFT_SYSTEM_PROMPT = """You are drafting email replies on behalf of Buck Adams,
owner of Hendrickson Construction (HCI), a high-end residential remodeling company in Aspen, CO.

Write professional, concise replies. Buck's tone is direct and friendly.
Keep drafts under 100 words unless the email requires a detailed response.
Do not make commitments about pricing, timelines, or awards without Buck's approval.
Sign off as: Buck Adams | Hendrickson Construction | buck@hendricksoninc.com"""


def draft_reply(subject: str, sender_name: str, body_preview: str, project: str) -> str:
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
                    f"Project: {project}\nFrom: {sender_name}\n"
                    f"Subject: {subject}\nEmail preview: {body_preview[:500]}\n\n"
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
        f"Hi {first_name},\n\nThank you for your email{proj_note}. I've received your message "
        f"and will review and follow up with you shortly.\n\n"
        f"Best,\nBuck Adams\nHendrickson Construction\nbuck@hendricksoninc.com"
    )


def _to_html(text: str) -> str:
    return "<br>".join(text.replace("\r", "").split("\n"))


# ── Main ───────────────────────────────────────────────────────────────────────

def run(max_emails: int = 30, create_drafts: bool = True) -> dict:
    print("\n=== Inbox Review (WF-006) ===")
    result = {
        "total_unread":    0,
        "processed":       0,
        "bids_captured":   0,
        "rfis_captured":   0,
        "submittals_captured": 0,
        "by_project":      {},
        "emails":          [],
        "errors":          [],
    }

    try:
        conn = psycopg2.connect(**DB, cursor_factory=psycopg2.extras.RealDictCursor)
    except Exception as e:
        conn = None
        result["errors"].append(f"DB connection failed: {e}")

    messages = get_unread_messages(top=max_emails)
    result["total_unread"] = len(messages)
    print(f"  Found {len(messages)} unread messages")

    for msg in messages:
        try:
            msg_id       = msg["id"]
            subject      = msg.get("subject", "(no subject)")
            preview      = msg.get("bodyPreview", "")
            sender       = (msg.get("from") or {}).get("emailAddress", {})
            sender_name  = sender.get("name", "")
            sender_email = sender.get("address", "")
            received     = msg.get("receivedDateTime", "")

            # 1 — Classify by project
            project = classify_email(subject, preview, sender_email)

            bid_written       = False
            rfi_written       = False
            submittal_written = False

            if conn:
                # 2 — Bid detection
                if _is_bid_email(subject, preview):
                    amount = _extract_dollar_amount(f"{subject} {preview}")
                    if amount and amount > 100:
                        bid_written = _write_bid_entry(
                            subject, sender_name, sender_email, preview,
                            project, amount, msg_id, conn
                        )
                        if bid_written:
                            result["bids_captured"] += 1

                # 3 — RFI detection (only if not already a bid)
                if not bid_written and _is_rfi_email(subject, preview):
                    rfi_written = _write_rfi(subject, sender_name, preview, project, msg_id, conn)
                    if rfi_written:
                        result["rfis_captured"] += 1

                # 4 — Submittal detection
                if not bid_written and not rfi_written and _is_submittal_email(subject, preview):
                    submittal_written = _write_submittal(
                        subject, sender_name, preview, project, msg_id, conn
                    )
                    if submittal_written:
                        result["submittals_captured"] += 1

            # 5 — Draft reply
            draft_id = None
            if create_drafts and not _is_automated_sender(sender_email):
                draft_text = draft_reply(subject, sender_name, preview, project)
                draft_html = _to_html(draft_text)
                try:
                    draft = create_reply_draft(msg_id, draft_html)
                    draft_id = draft.get("id")
                except Exception as e:
                    result["errors"].append(f"Draft failed ({subject[:40]}): {e}")

            # 6 — Move to folder
            folder_id = FOLDERS.get(project)
            moved = False
            if folder_id:
                _, err = move_message(msg_id, folder_id)
                moved = err is None
                if err:
                    result["errors"].append(f"Move failed ({subject[:40]}): {err}")

            # 7 — Track
            entry = {
                "subject":            subject,
                "from_name":          sender_name,
                "from_email":         sender_email,
                "received":           received,
                "project":            project,
                "moved":              moved,
                "draft_created":      draft_id is not None,
                "bid_captured":       bid_written,
                "rfi_captured":       rfi_written,
                "submittal_captured": submittal_written,
            }
            result["emails"].append(entry)
            result["by_project"].setdefault(project, []).append(entry)
            result["processed"] += 1

            tags = []
            if bid_written:       tags.append("BID")
            if rfi_written:       tags.append("RFI")
            if submittal_written: tags.append("SUBMITTAL")
            tag_str = f" [{','.join(tags)}]" if tags else ""
            print(f"  ✓ [{project}]{tag_str} {subject[:50]} — moved={moved}, draft={draft_id is not None}")

        except Exception as e:
            result["errors"].append(f"Email {msg.get('id','?')}: {e}")

    if conn:
        conn.close()

    result["status"] = "success" if not result["errors"] else "partial"
    print(f"  ✓ Inbox review done — {result['processed']} processed, "
          f"{result['bids_captured']} bids, {result['rfis_captured']} RFIs, "
          f"{result['submittals_captured']} submittals, {len(result['errors'])} errors")
    return result
