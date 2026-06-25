"""
HCI AI — HubSpot API client.
Pipeline: 2203777729
Stages: 3524209344=Not Started, 3524209345=Scope Ready, 3524209346=Sent Out,
        3524209347=Bids Receiving, 3524209348=Leveling, 3524209349=Awarded,
        3524209350=Not Awarded
"""
import json, time, urllib.error, urllib.request
from credentials import get_hubspot_auth


def _auth() -> str:
    return get_hubspot_auth()


def _request(method: str, path: str, body: dict = None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(f"https://api.hubapi.com{path}", data=data, method=method)
    req.add_header("Authorization", _auth())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
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
