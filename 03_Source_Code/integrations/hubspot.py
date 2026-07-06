"""
HCI AI — HubSpot API client.
Pipeline: 2203777729
Stages: 3524209344=Not Started, 3524209345=Scope Ready, 3524209346=Sent Out,
        3524209347=Bids Receiving, 3524209348=Leveling, 3524209349=Awarded,
        3524209350=Not Awarded
"""
import json, ssl, time, urllib.error, urllib.request
import certifi
from credentials import get_hubspot_auth

SSL_CTX = ssl.create_default_context(cafile=certifi.where())


def _auth() -> str:
    return get_hubspot_auth()


def _request(method: str, path: str, body: dict = None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"https://api.hubapi.com{path}", data=data, method=method)
    req.add_header("Authorization", _auth())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as r:
            return json.loads(r.read()), None
    except urllib.error.HTTPError as e:
        return None, f"{e.code}: {e.read().decode()[:300]}"


def get_deal(deal_id: str) -> dict:
    r, _ = _request("GET", f"/crm/v3/objects/deals/{deal_id}?properties=dealname,dealstage,amount")
    return r


def patch_deal(deal_id: str, properties: dict):
    return _request("PATCH", f"/crm/v3/objects/deals/{deal_id}", {"properties": properties})


def create_task(subject: str, body: str, due_date_ms: int, owner_id: str = None):
    props = {
        "hs_task_subject": subject,
        "hs_task_body": body,
        "hs_task_status": "NOT_STARTED",
        "hs_task_type": "TODO",
        "hs_timestamp": due_date_ms,
    }
    if owner_id:
        props["hubspot_owner_id"] = owner_id
    return _request("POST", "/crm/v3/objects/tasks", {"properties": props})


def add_note(deal_id: str, note_body: str):
    payload = {
        "engagement": {"active": True, "type": "NOTE", "timestamp": int(time.time() * 1000)},
        "associations": {"contactIds": [], "companyIds": [], "dealIds": [int(deal_id)], "ownerIds": []},
        "metadata": {"body": note_body},
    }
    return _request("POST", "/engagements/v1/engagements", payload)


# Pipeline stage constants
STAGE = {
    "not_started":    "3524209344",
    "scope_ready":    "3524209345",
    "sent_out":       "3524209346",
    "bids_receiving": "3524209347",
    "leveling":       "3524209348",
    "awarded":        "3524209349",
    "not_awarded":    "3524209350",
}

PIPELINE_ID = "2203777729"


def create_deal(name: str, stage_key: str = "not_started", amount: float = None) -> tuple:
    props = {
        "dealname":    name,
        "pipeline":    PIPELINE_ID,
        "dealstage":   STAGE[stage_key],
    }
    if amount is not None:
        props["amount"] = str(amount)
    return _request("POST", "/crm/v3/objects/deals", {"properties": props})


_owners_cache: dict | None = None

def get_owner_name(owner_id: str | None) -> str | None:
    """Resolve a HubSpot hubspot_owner_id to a real name via /crm/v3/owners.
    Found 2026-07-06: hubspot_deals.owner was blank for all 310 synced deals -
    sync_hubspot.py's get_all_deals()/upsert_deal() never requested or stored
    hubspot_owner_id at all. Not a HubSpot data gap - confirmed via live HubSpot UI
    (Buck/GBT) that owners ARE populated for most deals (Chris Hendrickson, Tim
    Johns, Michael Mount, Trafford Melville, Frankie Arvesen); only 101F Roofing
    and 101F Windows are genuinely ownerless. This app's token lacks the Owners
    API scope (confirmed: 403 on /crm/v3/owners) - falls back to the raw numeric
    ID so at least *something* non-blank is stored until that scope is granted."""
    global _owners_cache
    if not owner_id:
        return None
    if _owners_cache is None:
        _owners_cache = {}
        try:
            after = None
            while True:
                path = "/crm/v3/owners?limit=100" + (f"&after={after}" if after else "")
                r, err = _request("GET", path)
                if err or not r:
                    break
                for o in r.get("results", []):
                    name = f"{o.get('firstName','')} {o.get('lastName','')}".strip() or o.get("email", "")
                    _owners_cache[str(o["id"])] = name
                after = (r.get("paging") or {}).get("next", {}).get("after")
                if not after:
                    break
        except Exception:
            pass
    return _owners_cache.get(str(owner_id))


def get_overdue_tasks(limit: int = 20) -> list:
    import time
    now_ms = int(time.time() * 1000)
    r, _ = _request("GET", f"/crm/v3/objects/tasks?limit={limit}"
                    f"&properties=hs_task_subject,hs_task_status,hs_timestamp,hs_task_body"
                    f"&filterGroups=%5B%7B%22filters%22%3A%5B%7B%22propertyName%22%3A%22hs_task_status%22%2C%22operator%22%3A%22EQ%22%2C%22value%22%3A%22NOT_STARTED%22%7D%5D%7D%5D")
    results = (r or {}).get("results", [])
    overdue = []
    for t in results:
        ts = t.get("properties", {}).get("hs_timestamp")
        if ts and int(ts) < now_ms:
            overdue.append(t)
    return overdue
