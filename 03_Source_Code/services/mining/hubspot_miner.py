"""
HubSpot Miner — reads HubSpot DB tables (already synced) for project/vendor/deal changes.
Extracts: deal stage changes, new contacts, task completions.
Writes to: background_learning_records, approval_queue (project brain updates queued).
Source is READ-ONLY — never writes back to HubSpot.
"""
from .base_miner import BaseMiner, MiningResult


class HubSpotMiner(BaseMiner):
    MINER_NAME = "hubspot_miner"
    SOURCE_SYSTEMS = ["hubspot"]
    TARGET_STORES = ["background_learning_records", "approval_queue"]

    def mine(self) -> MiningResult:
        run_id = self.start_run()
        result = MiningResult(self.MINER_NAME, run_id)
        try:
            deals = self._mine_deals(result)
            contacts = self._mine_contacts(result)
            tasks = self._mine_tasks(result)
            result.summary = {
                "deals_scanned": deals,
                "contacts_scanned": contacts,
                "tasks_scanned": tasks,
            }
            return self.complete_run(run_id, result)
        except Exception as e:
            return self.fail_run(run_id, str(e))

    def _mine_deals(self, result: MiningResult) -> int:
        deals = self._query("""
            SELECT d.hubspot_deal_id, d.deal_name, d.stage, d.amount,
                   p.id as project_id, p.name as project_name
            FROM hubspot_deals d
            LEFT JOIN projects p ON p.hubspot_deal_id = d.hubspot_deal_id
            ORDER BY d.last_modified DESC NULLS LAST
            LIMIT 50
        """)
        result.records_scanned += len(deals)

        for deal in deals:
            # Register each deal as a BL record if not already tracked
            rec_id = self.register_discovery(
                source_system="hubspot",
                source_id=str(deal["hubspot_deal_id"]),
                source_name=deal["deal_name"] or f"Deal {deal['hubspot_deal_id']}",
                project_id=deal["project_id"],
                metadata={"stage": deal["stage"], "amount": str(deal["amount"] or "")}
            )
            if rec_id:
                result.records_discovered += 1

        return len(deals)

    def _mine_contacts(self, result: MiningResult) -> int:
        contacts = self._query("""
            SELECT c.hubspot_contact_id, c.first_name, c.last_name, c.company,
                   c.email, c.phone, c.job_title
            FROM hubspot_contacts c
            ORDER BY c.synced_at DESC NULLS LAST
            LIMIT 100
        """)
        result.records_scanned += len(contacts)

        for contact in contacts:
            name = f"{contact['first_name'] or ''} {contact['last_name'] or ''}".strip()
            company = contact.get("company", "")
            if not name and not company:
                continue
            # Check if this contact maps to a vendor we don't have yet
            if company:
                existing = self._query_one(
                    "SELECT id FROM vendors WHERE company_name ILIKE %s LIMIT 1",
                    (f"%{company}%",)
                )
                if not existing:
                    # Queue as a vendor candidate for Buck to approve
                    self.queue_for_approval(
                        action_type="vendor_candidate",
                        title=f"New vendor candidate: {company}",
                        description=(
                            f"HubSpot contact {name} ({contact.get('email','')}) "
                            f"is associated with company '{company}'. "
                            "Approve to add to Vendor Registry."
                        ),
                        payload={
                            "company_name": company,
                            "contact_name": name,
                            "email": contact.get("email"),
                            "phone": contact.get("phone"),
                            "hubspot_contact_id": contact["hubspot_contact_id"],
                        },
                        priority="low"
                    )
                    result.items_queued_for_review += 1
                    result.intelligence_extracted += 1

        return len(contacts)

    def _mine_tasks(self, result: MiningResult) -> int:
        tasks = self._query("""
            SELECT t.hubspot_task_id, t.subject, t.status, t.due_timestamp
            FROM hubspot_tasks t
            WHERE t.status = 'COMPLETED'
            ORDER BY t.synced_at DESC NULLS LAST
            LIMIT 50
        """)
        result.records_scanned += len(tasks)

        completed_important = [
            t for t in tasks
            if any(kw in (t.get("subject") or "").lower()
                   for kw in ["bid", "award", "contract", "inspection", "punch", "closeout"])
        ]
        result.intelligence_extracted += len(completed_important)
        result.summary["completed_key_tasks"] = len(completed_important)
        return len(tasks)
