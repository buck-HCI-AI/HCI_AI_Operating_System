"""
HubSpot Connector — Direct API Pull (no Browser Agent)

Pulls Contacts, Companies, Deals, Activities from HubSpot v3 API.
READ-ONLY: never writes back to HubSpot without explicit human approval.

Incremental sync: lastmodifieddate >= last_synced_at (ms timestamp).
Pagination:      cursor-based via paging.next.after.
Activities:      CALL, EMAIL, MEETING, NOTE, TASK fetched separately, merged under 'activities'.
"""

import os, ssl, json, logging, urllib.request, urllib.error
from datetime import datetime, timezone
from typing import Optional

import certifi
from base_connector import BaseConnector, ConnectorResult

logger = logging.getLogger("hci.connector.hubspot")

_HS_BASE = "https://api.hubapi.com"

_CONTACT_PROPS  = ["firstname","lastname","email","phone","jobtitle","company","hs_lead_status","lifecyclestage","lastmodifieddate"]
_COMPANY_PROPS  = ["name","domain","phone","industry","type","city","state","zip","lastmodifieddate"]
_DEAL_PROPS     = ["dealname","amount","dealstage","pipeline","closedate","hci_project_code","lastmodifieddate"]
_CALL_PROPS     = ["hs_call_title","hs_call_body","hs_call_duration","hs_call_disposition","hs_timestamp","hs_lastmodifieddate"]
_EMAIL_PROPS    = ["hs_email_subject","hs_email_text","hs_timestamp","hs_lastmodifieddate"]
_MEETING_PROPS  = ["hs_meeting_title","hs_meeting_body","hs_timestamp","hs_meeting_outcome","hs_lastmodifieddate"]
_NOTE_PROPS     = ["hs_note_body","hs_timestamp","hs_lastmodifieddate"]
_TASK_PROPS     = ["hs_task_subject","hs_task_body","hs_task_status","hs_timestamp","hs_lastmodifieddate"]

_ACTIVITY_MAP = {
    "calls":    (_CALL_PROPS,    "hs_call_title",    "hs_call_body",    "hs_call_duration", "hs_call_disposition", "hs_timestamp"),
    "emails":   (_EMAIL_PROPS,   "hs_email_subject", "hs_email_text",   None,               None,                  "hs_timestamp"),
    "meetings": (_MEETING_PROPS, "hs_meeting_title", "hs_meeting_body", None,               "hs_meeting_outcome",  "hs_timestamp"),
    "notes":    (_NOTE_PROPS,    None,               "hs_note_body",    None,               None,                  "hs_timestamp"),
    "tasks":    (_TASK_PROPS,    "hs_task_subject",  "hs_task_body",    None,               "hs_task_status",      "hs_timestamp"),
}

_REQUIRED = {
    "contacts":   ["hubspot_id"],
    "companies":  ["hubspot_id"],
    "deals":      ["hubspot_id"],
    "activities": ["hubspot_id", "activity_type"],
}


def _token() -> str:
    t = os.environ.get("HUBSPOT_API_KEY", "")
    if not t:
        raise RuntimeError("HUBSPOT_API_KEY not set in environment")
    return t


def _hs_request(path: str, method: str = "GET", body: Optional[dict] = None) -> dict:
    url = f"{_HS_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data,
        headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"},
        method=method,
    )
    ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
        return json.loads(resp.read().decode())


def _fetch_objects(object_type: str, properties: list, since_ms: Optional[str] = None, limit: int = 100) -> list:
    """Paginate all pages; optionally filter by lastmodifieddate >= since_ms (ms string)."""
    results = []
    after = None
    if since_ms:
        while True:
            body: dict = {
                "filterGroups": [{"filters": [{"propertyName": "lastmodifieddate", "operator": "GTE", "value": since_ms}]}],
                "properties": properties, "limit": limit,
            }
            if after:
                body["after"] = after
            page = _hs_request(f"/crm/v3/objects/{object_type}/search", method="POST", body=body)
            results.extend(page.get("results", []))
            after = page.get("paging", {}).get("next", {}).get("after")
            if not after:
                break
    else:
        while True:
            path = f"/crm/v3/objects/{object_type}?properties={','.join(properties)}&limit={limit}"
            if after:
                path += f"&after={after}"
            page = _hs_request(path)
            results.extend(page.get("results", []))
            after = page.get("paging", {}).get("next", {}).get("after")
            if not after:
                break
    return results


def _fetch_activities(since_ms: Optional[str] = None) -> list:
    records = []
    for hs_type, (props, subj_k, body_k, dur_k, outcome_k, ts_k) in _ACTIVITY_MAP.items():
        raw_type = hs_type.rstrip("s").upper()
        try:
            items = _fetch_objects(hs_type, props, since_ms=since_ms)
            for item in items:
                p = item.get("properties", {})
                records.append({
                    "hubspot_id":    f"{raw_type}:{item['id']}",
                    "activity_type": raw_type,
                    "subject":       p.get(subj_k) if subj_k else None,
                    "body":          p.get(body_k) if body_k else None,
                    "activity_ts":   p.get(ts_k),
                    "duration_ms":   int(p[dur_k]) if dur_k and p.get(dur_k) else None,
                    "outcome":       p.get(outcome_k) if outcome_k else None,
                    "raw_properties": p,
                })
        except Exception as e:
            logger.warning("hubspot activities/%s fetch failed: %s", hs_type, e)
    return records


class HubSpotConnector(BaseConnector):
    name = "hubspot"
    version = "1.0"
    supported_entities = ["contacts", "companies", "deals", "activities"]

    def sync(self, entity_types: Optional[list] = None, dry_run: Optional[bool] = None) -> dict:
        """Fetch from HubSpot API and ingest. Uses last_synced_at as incremental watermark."""
        types = entity_types or self.supported_entities
        if dry_run is not None:
            self.dry_run = dry_run

        payload: dict = {}
        for entity_type in types:
            state = self.get_sync_state(entity_type)
            since_ms = None
            if state and state.get("last_synced_at"):
                dt = state["last_synced_at"]
                if hasattr(dt, "timestamp"):
                    since_ms = str(int(dt.timestamp() * 1000))
            try:
                if entity_type == "contacts":
                    raw = _fetch_objects("contacts", _CONTACT_PROPS, since_ms=since_ms)
                    payload["contacts"] = [
                        {"hubspot_id": r["id"], **{
                            k: r["properties"].get(k) for k in
                            ["firstname","lastname","email","phone","jobtitle","hs_lead_status","lifecyclestage"]
                        }, "company_name": r["properties"].get("company"),
                        "raw_properties": r["properties"]}
                        for r in raw
                    ]
                elif entity_type == "companies":
                    raw = _fetch_objects("companies", _COMPANY_PROPS, since_ms=since_ms)
                    payload["companies"] = [
                        {"hubspot_id": r["id"], **{
                            k: r["properties"].get(k) for k in
                            ["name","domain","phone","industry","type","city","state","zip"]
                        }, "raw_properties": r["properties"]}
                        for r in raw
                    ]
                elif entity_type == "deals":
                    raw = _fetch_objects("deals", _DEAL_PROPS, since_ms=since_ms)
                    payload["deals"] = [
                        {"hubspot_id": r["id"], **{
                            k: r["properties"].get(k) for k in
                            ["dealname","amount","dealstage","pipeline","closedate"]
                        }, "project_code": r["properties"].get("hci_project_code"),
                        "raw_properties": r["properties"]}
                        for r in raw
                    ]
                elif entity_type == "activities":
                    payload["activities"] = _fetch_activities(since_ms=since_ms)
            except Exception as e:
                logger.error("hubspot sync/%s fetch error: %s", entity_type, e)

        if not payload:
            return {"status": "no_data", "entity_types_attempted": types, "dry_run": self.dry_run}
        return self.ingest(payload)

    # ── Abstract method implementations (per-record, matching BaseConnector contract) ──

    def validate(self, entity_type: str, record: dict) -> tuple[bool, list]:
        required = _REQUIRED.get(entity_type, ["hubspot_id"])
        missing = [f for f in required if not record.get(f)]
        return (not missing), missing

    def normalize(self, entity_type: str, record: dict) -> dict:
        r = dict(record)
        if "amount" in r and r["amount"]:
            try:
                r["amount"] = float(str(r["amount"]).replace("$","").replace(",","").strip())
            except (ValueError, TypeError):
                r["amount"] = None
        if "closedate" in r and r["closedate"]:
            try:
                cd = r["closedate"]
                if isinstance(cd, str) and len(cd) > 10:
                    r["closedate"] = cd[:10]
                elif isinstance(cd, (int, float)):
                    r["closedate"] = datetime.fromtimestamp(cd/1000, tz=timezone.utc).date().isoformat()
            except Exception:
                r["closedate"] = None
        if "activity_ts" in r and r["activity_ts"]:
            try:
                ts = r["activity_ts"]
                if isinstance(ts, str) and ts.isdigit():
                    r["activity_ts"] = datetime.fromtimestamp(int(ts)/1000, tz=timezone.utc).isoformat()
                elif isinstance(ts, (int, float)):
                    r["activity_ts"] = datetime.fromtimestamp(ts/1000, tz=timezone.utc).isoformat()
            except Exception:
                r["activity_ts"] = None
        return r

    def persist(self, entity_type: str, record: dict, cur) -> bool:
        fn = {
            "contacts":   self._persist_contact,
            "companies":  self._persist_company,
            "deals":      self._persist_deal,
            "activities": self._persist_activity,
        }.get(entity_type)
        if not fn:
            raise NotImplementedError(f"No persist handler for {entity_type}")
        return fn(record, cur)

    def _upsert(self, cur, sql: str, params: tuple) -> bool:
        cur.execute(sql, params)
        row = cur.fetchone()
        return bool(row and row.get("is_insert"))

    def _persist_contact(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO hubspot_contacts
                (hubspot_id, firstname, lastname, email, phone, jobtitle,
                 company_name, hs_lead_status, lifecyclestage, raw_properties, synced_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
            ON CONFLICT (hubspot_id) DO UPDATE SET
                firstname       = EXCLUDED.firstname,
                lastname        = EXCLUDED.lastname,
                email           = EXCLUDED.email,
                phone           = COALESCE(EXCLUDED.phone, hubspot_contacts.phone),
                jobtitle        = COALESCE(EXCLUDED.jobtitle, hubspot_contacts.jobtitle),
                company_name    = COALESCE(EXCLUDED.company_name, hubspot_contacts.company_name),
                hs_lead_status  = EXCLUDED.hs_lead_status,
                lifecyclestage  = EXCLUDED.lifecyclestage,
                raw_properties  = EXCLUDED.raw_properties,
                synced_at       = NOW(),
                updated_at      = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r["hubspot_id"], r.get("firstname"), r.get("lastname"), r.get("email"),
            r.get("phone"), r.get("jobtitle"), r.get("company_name"),
            r.get("hs_lead_status"), r.get("lifecyclestage"),
            json.dumps(r.get("raw_properties") or {}),
        ))

    def _persist_company(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO hubspot_companies
                (hubspot_id, name, domain, phone, industry, type, city, state, zip, raw_properties, synced_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
            ON CONFLICT (hubspot_id) DO UPDATE SET
                name           = EXCLUDED.name,
                domain         = COALESCE(EXCLUDED.domain, hubspot_companies.domain),
                phone          = COALESCE(EXCLUDED.phone, hubspot_companies.phone),
                industry       = COALESCE(EXCLUDED.industry, hubspot_companies.industry),
                type           = COALESCE(EXCLUDED.type, hubspot_companies.type),
                city           = COALESCE(EXCLUDED.city, hubspot_companies.city),
                state          = COALESCE(EXCLUDED.state, hubspot_companies.state),
                zip            = COALESCE(EXCLUDED.zip, hubspot_companies.zip),
                raw_properties = EXCLUDED.raw_properties,
                synced_at      = NOW(),
                updated_at     = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r["hubspot_id"], r.get("name"), r.get("domain"), r.get("phone"),
            r.get("industry"), r.get("type"), r.get("city"), r.get("state"),
            r.get("zip"), json.dumps(r.get("raw_properties") or {}),
        ))

    def _persist_deal(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO hubspot_deals
                (hubspot_id, dealname, amount, dealstage, pipeline, closedate, project_code, raw_properties, synced_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
            ON CONFLICT (hubspot_id) DO UPDATE SET
                dealname       = EXCLUDED.dealname,
                amount         = COALESCE(EXCLUDED.amount, hubspot_deals.amount),
                dealstage      = EXCLUDED.dealstage,
                pipeline       = EXCLUDED.pipeline,
                closedate      = COALESCE(EXCLUDED.closedate, hubspot_deals.closedate),
                project_code   = COALESCE(EXCLUDED.project_code, hubspot_deals.project_code),
                raw_properties = EXCLUDED.raw_properties,
                synced_at      = NOW(),
                updated_at     = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r["hubspot_id"], r.get("dealname"), r.get("amount"), r.get("dealstage"),
            r.get("pipeline"), r.get("closedate"), r.get("project_code"),
            json.dumps(r.get("raw_properties") or {}),
        ))

    def _persist_activity(self, r: dict, cur) -> bool:
        return self._upsert(cur, """
            INSERT INTO hubspot_activities
                (hubspot_id, activity_type, subject, body, activity_ts, duration_ms, outcome,
                 associated_contact_id, associated_deal_id, associated_company_id,
                 raw_properties, synced_at, updated_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW())
            ON CONFLICT (hubspot_id) DO UPDATE SET
                subject               = COALESCE(EXCLUDED.subject, hubspot_activities.subject),
                body                  = COALESCE(EXCLUDED.body, hubspot_activities.body),
                activity_ts           = EXCLUDED.activity_ts,
                duration_ms           = COALESCE(EXCLUDED.duration_ms, hubspot_activities.duration_ms),
                outcome               = COALESCE(EXCLUDED.outcome, hubspot_activities.outcome),
                associated_contact_id = COALESCE(EXCLUDED.associated_contact_id, hubspot_activities.associated_contact_id),
                associated_deal_id    = COALESCE(EXCLUDED.associated_deal_id, hubspot_activities.associated_deal_id),
                associated_company_id = COALESCE(EXCLUDED.associated_company_id, hubspot_activities.associated_company_id),
                raw_properties        = EXCLUDED.raw_properties,
                synced_at             = NOW(),
                updated_at            = NOW()
            RETURNING (xmax=0) AS is_insert
        """, (
            r["hubspot_id"], r.get("activity_type"), r.get("subject"), r.get("body"),
            r.get("activity_ts"), r.get("duration_ms"), r.get("outcome"),
            r.get("associated_contact_id"), r.get("associated_deal_id"), r.get("associated_company_id"),
            json.dumps(r.get("raw_properties") or {}),
        ))
