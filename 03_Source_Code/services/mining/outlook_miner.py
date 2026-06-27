"""
Outlook Communications Miner — reads recent emails via Graph API.
Filters for bid activity, vendor communications, project correspondence.
Extracts: bid responses, vendor quotes, RFI emails.
Writes to: background_learning_records, approval_queue (procurement items queued).
Outlook is READ-ONLY — never sends emails or modifies mailbox.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "integrations"))

from .base_miner import BaseMiner, MiningResult

_BID_KEYWORDS = ["bid", "quote", "proposal", "pricing", "estimate", "per your request"]
_VENDOR_KEYWORDS = ["sub", "subcontractor", "supplier", "vendor", "material", "delivery"]
_PROJECT_KEYWORDS = ["eastwood", "francis", "riverside", "sagebrusch", "64ew", "101f", "1355r"]
_RFI_KEYWORDS = ["rfi", "request for information", "clarification", "submittal", "shop drawing"]
_HIGH_PRIORITY_KEYWORDS = ["award", "contract", "change order", "change directive", "amendment"]


def _classify_email(subject: str, body_preview: str = "") -> tuple:
    text = (subject + " " + body_preview).lower()
    if any(kw in text for kw in _HIGH_PRIORITY_KEYWORDS):
        return "contract_action", "high"
    if any(kw in text for kw in _RFI_KEYWORDS):
        return "rfi_correspondence", "medium"
    if any(kw in text for kw in _BID_KEYWORDS):
        return "bid_correspondence", "medium"
    if any(kw in text for kw in _VENDOR_KEYWORDS):
        return "vendor_communication", "low"
    return None, None


def _infer_project_from_email(subject: str, body: str = "") -> tuple:
    text = (subject + " " + body).lower()
    if "eastwood" in text or "64ew" in text:
        return 1, "64 Eastwood"
    if "francis" in text or "101f" in text:
        return 2, "101 Francis"
    if "riverside" in text or "1355" in text:
        return 3, "1355 Riverside"
    if "sagebrusch" in text or "83sb" in text:
        return 4, "83 Sagebrusch"
    return None, None


class OutlookMiner(BaseMiner):
    MINER_NAME = "outlook_miner"
    SOURCE_SYSTEMS = ["outlook"]
    TARGET_STORES = ["background_learning_records", "procurement_items", "approval_queue"]

    def mine(self) -> MiningResult:
        run_id = self.start_run()
        result = MiningResult(self.MINER_NAME, run_id)
        try:
            emails = self._fetch_emails()
            result.records_scanned = len(emails)

            for email in emails:
                subject = email.get("subject", "") or ""
                preview = email.get("bodyPreview", "") or ""
                email_id = email.get("id", "")
                sender = (email.get("from") or {}).get("emailAddress", {})
                sender_name = sender.get("name", "")
                sender_email = sender.get("address", "")
                received = email.get("receivedDateTime", "")

                email_type, priority = _classify_email(subject, preview)
                if not email_type:
                    continue

                project_id, project_name = _infer_project_from_email(subject, preview)

                self.register_discovery(
                    source_system="outlook",
                    source_id=email_id,
                    source_name=f"{email_type}: {subject[:80]}",
                    project_id=project_id,
                    metadata={"email_type": email_type, "sender": sender_email,
                               "received": received, "subject": subject[:200]}
                )
                result.records_discovered += 1

                self.queue_for_approval(
                    action_type=email_type,
                    title=f"{email_type.replace('_',' ').title()}: {subject[:80]}",
                    description=(
                        f"From: {sender_name} <{sender_email}>\n"
                        f"Received: {received}\n"
                        f"Project: {project_name or 'Unknown'}\n\n"
                        f"Preview: {preview[:400]}"
                    ),
                    payload={"email_id": email_id, "subject": subject,
                             "sender_email": sender_email, "received": received,
                             "email_type": email_type, "project_id": project_id},
                    project_id=project_id,
                    priority=priority
                )
                result.items_queued_for_review += 1
                result.intelligence_extracted += 1

            result.summary = {
                "emails_scanned": len(emails),
                "relevant_emails": result.records_discovered,
                "queued_for_review": result.items_queued_for_review,
            }
            return self.complete_run(run_id, result)

        except Exception as e:
            result.summary["error_detail"] = str(e)
            return self.fail_run(run_id, str(e))

    def _fetch_emails(self) -> list:
        try:
            from microsoft_graph import list_inbox
            return list_inbox(top=50) or []
        except Exception:
            return []
